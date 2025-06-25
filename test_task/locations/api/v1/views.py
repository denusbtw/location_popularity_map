import pandas as pd

from django.db.models import Avg, Count, F
from django.http import HttpResponse
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
        queryset = queryset.annotate(average_rating=Avg("reviews__rating"))
        queryset = queryset.annotate(review_count=Count("reviews"))

        rating_weight = 0.6
        reviews_weight = 0.3
        views_weight = 0.1

        queryset = queryset.annotate(
            popularity_score=(
                F("average_rating") * rating_weight
                + F("review_count") * reviews_weight
                + F("view_count") * views_weight
            )
        )

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

    def get_serializer_class(self):
        if self.request.method == "POST":
            return LocationCreateSerializer
        return LocationListSerializer


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
