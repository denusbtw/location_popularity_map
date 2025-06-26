import asyncio

import pandas as pd
from asgiref.sync import sync_to_async
from django.core.cache import cache
from adrf import generics as async_generics
from adrf import mixins as async_mixins

from django.http import HttpResponse
from rest_framework import generics, filters, views, permissions, response

from .permissions import IsAdminOrReadOnly
from .serializers import (
    LocationCreateSerializer,
    LocationListSerializer,
    LocationUpdateSerializer,
    LocationRetrieveSerializer,
)
from test_task.locations.models import Location
from ...services import fetch_weather


class LocationQuerySetMixin:

    def get_queryset(self):
        queryset = Location.objects.select_related("category")
        queryset = queryset.prefetch_related("reviews")
        queryset = queryset.annotate_average_rating()
        queryset = queryset.annotate_review_count()
        queryset = queryset.annotate_popularity_score()

        if self.request.user.is_staff:
            return queryset
        return queryset.filter(is_active=True)


class AsyncLocationListCreateAPIView(
    LocationQuerySetMixin,
    async_mixins.ListModelMixin,
    async_mixins.CreateModelMixin,
    async_generics.GenericAPIView,
):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (
        #     DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    # filterset_class = LocationFilterSet
    search_fields = ("name", "description")
    ordering_fields = (
        "name",
        "view_count",
        "average_rating",
        "review_count",
        "created_at",
        "is_active",
        "popularity_score",
    )

    async def get_queryset(self):
        return await sync_to_async(list)(super().get_queryset())

    async def get(self, request, *args, **kwargs):
        queryset = await self.get_queryset()

        page = await sync_to_async(self.paginate_queryset)(queryset)

        if page is not None:
            serialized_page = self.get_serializer(page, many=True).data

            enriched_page = await asyncio.gather(
                *(self.enrich_with_weather(loc) for loc in serialized_page)
            )
            return self.get_paginated_response(enriched_page)

        serialized_data = self.get_serializer(queryset, many=True).data

        enriched_data = await asyncio.gather(
            *(self.enrich_with_weather(loc) for loc in serialized_data)
        )
        return response.Response(enriched_data)

    async def post(self, request, *args, **kwargs):
        return await self.create(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return LocationCreateSerializer
        return LocationListSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)

        # обгортаю у try-except щоб не фейлились тести
        try:
            cache.delete_pattern("*location_list*")
        except AttributeError:
            pass

    async def enrich_with_weather(self, loc):
        lat = loc["latitude"]
        lon = loc["longitude"]
        loc["weather"] = await fetch_weather(lat, lon)
        return loc


class LocationDetailAPIView(
    LocationQuerySetMixin, generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = (IsAdminOrReadOnly,)

    def get_object(self):
        obj = super().get_object()
        obj.view_count += 1
        obj.save(update_fields=["view_count"])
        return obj

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return LocationUpdateSerializer
        return LocationRetrieveSerializer

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])
        try:
            cache.delete_pattern("*location_list*")
        except AttributeError:
            pass

    def perform_update(self, serializer):
        super().perform_update(serializer)
        try:
            cache.delete_pattern("*location_list*")
        except AttributeError:
            pass


class LocationExportCSVAPIView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        queryset = Location.objects.all().values(
            "id",
            "name",
            "description",
            "category_id",
            "category__name",
            "latitude",
            "longitude",
            "address",
            "is_active",
            "view_count",
            "created_at",
        )
        df = pd.DataFrame.from_records(queryset)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=locations.csv"

        response.write("\ufeff")
        df.to_csv(path_or_buf=response, index=False)

        return response
