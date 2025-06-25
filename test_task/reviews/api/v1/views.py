from django.conf import settings
from django.db.models import Q
from django.db.models.aggregates import Count
from django.db.models.fields import IntegerField
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, permissions, views

from django.core.cache import cache

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
        queryset = Review.objects.filter(location_id=self.kwargs["location_id"])
        queryset = queryset.annotate(
            upvote_count=Count(
                "votes",
                Q(votes__vote=ReviewVote.Vote.UPVOTE),
                output_field=IntegerField(),
            ),
        )
        queryset = queryset.annotate(
            downvote_count=Count(
                "votes",
                Q(votes__vote=ReviewVote.Vote.DOWNVOTE),
                output_field=IntegerField(),
            ),
        )
        return queryset


class ReviewListCreateAPIView(ReviewQuerySetMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReviewCreateSerializer
        return ReviewListSerializer

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
