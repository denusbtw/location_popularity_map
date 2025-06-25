import pandas as pd
from django.conf import settings
from django.core import cache

from django.db.models import Avg, Count, F
from django.db.models.fields import FloatField
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, views, permissions
from .filters import LocationFilterSet
from .permissions import IsAdminOrReadOnly
from .serializers import (
    LocationCreateSerializer,
    LocationListSerializer,
    LocationUpdateSerializer,
    LocationRetrieveSerializer,
)
from test_task.locations.models import Location


class LocationQuerySetMixin:

    def get_queryset(self):
        queryset = Location.objects.all()
        queryset = queryset.annotate_average_rating()
        queryset = queryset.annotate_review_count()
        queryset = queryset.annotate_popularity_score()

        if self.request.user.is_staff:
            return queryset
        return queryset.filter(is_active=True)


class LocationListCreateAPIView(LocationQuerySetMixin, generics.ListCreateAPIView):
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_class = LocationFilterSet
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

    @method_decorator(cache_page(settings.CACHE_TTL, key_prefix="location_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return LocationCreateSerializer
        return LocationListSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)
        cache.delete_pattern("*location_list*")


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
        cache.delete_pattern("*location_list*")

    def perform_update(self, serializer):
        super().perform_update(serializer)
        cache.delete_pattern("*location_list*")


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
