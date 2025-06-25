from rest_framework import generics, permissions

from .permissions import IsUser
from .serializers import (
    ReviewListSerializer,
    ReviewCreateSerializer,
    ReviewRetrieveSerializer,
    ReviewUpdateSerializer,
)
from test_task.reviews.models import Review


class ReviewQuerySetMixin:

    def get_queryset(self):
        return Review.objects.filter(location_id=self.request.kwargs["location_id"])


class ReviewListCreateAPIView(ReviewQuerySetMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReviewListSerializer
        return ReviewCreateSerializer

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            location_id=self.kwargs["location_id"],
        )


class ReviewDetailAPIView(ReviewQuerySetMixin, generics.RetrieveUpdateDestroyAPIView):

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ReviewRetrieveSerializer
        return ReviewUpdateSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        elif self.request.method in {"PUT", "PATCH"}:
            return [IsUser()]
        else:
            return [permissions.IsAdminUser()]
