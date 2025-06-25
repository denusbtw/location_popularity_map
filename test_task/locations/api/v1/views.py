from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters

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
        queryset = Location.objects.annotate(
            average_rating=Avg("reviews__rating"),
            review_count=Count("reviews"),
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
