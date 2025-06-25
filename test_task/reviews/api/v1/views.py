from rest_framework import generics, permissions, views

from .permissions import IsUser
from .serializers import (
    ReviewListSerializer,
    ReviewCreateSerializer,
    ReviewRetrieveSerializer,
    ReviewUpdateSerializer,
    ReviewVoteCreateSerializer,
    ReviewVoteUpdateSerializer,
)
from test_task.reviews.models import Review, ReviewVote


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


class ReviewVoteCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewVoteCreateSerializer

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            review_id=self.kwargs["review_id"],
        )


class ReviewVoteDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewVoteUpdateSerializer
    permission_classes = [IsUser]

    def get_queryset(self):
        return ReviewVote.objects.filter(
            user=self.request.user,
            review_id=self.kwargs["review_id"],
        )
