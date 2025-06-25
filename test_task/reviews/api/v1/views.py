from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, permissions

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
        queryset = queryset.select_related("location", "user")
        queryset = queryset.prefetch_related("votes")
        queryset = queryset.annotate_upvote_count()
        queryset = queryset.annotate_downvote_count()
        return queryset


class ReviewListCreateAPIView(ReviewQuerySetMixin, generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @method_decorator(cache_page(settings.CACHE_TTL, key_prefix="review_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReviewCreateSerializer
        return ReviewListSerializer

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            location_id=self.kwargs["location_id"],
        )
        try:
            cache.delete_pattern("*location_list*")
            cache.delete_pattern("*review_list*")
        except AttributeError:
            pass


class ReviewDetailAPIView(ReviewQuerySetMixin, generics.RetrieveUpdateDestroyAPIView):

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ReviewRetrieveSerializer
        return ReviewUpdateSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            self.permission_classes = [permissions.AllowAny]
        elif self.request.method in {"PUT", "PATCH"}:
            self.permission_classes = [IsUser]
        else:
            self.permission_classes = [permissions.IsAdminUser | IsUser]
        return super().get_permissions()

    def perform_update(self, serializer):
        super().perform_update(serializer)
        try:
            cache.delete_pattern("*location_list*")
            cache.delete_pattern("*review_list*")
        except AttributeError:
            pass

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        try:
            cache.delete_pattern("*location_list*")
            cache.delete_pattern("*review_list*")
        except AttributeError:
            pass


class ReviewVoteCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewVoteCreateSerializer

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            review_id=self.kwargs["review_id"],
        )
        try:
            cache.delete_pattern("*location_list*")
            cache.delete_pattern("*review_list*")
        except AttributeError:
            pass


class ReviewVoteDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewVoteUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsUser]

    def get_queryset(self):
        return ReviewVote.objects.filter(
            user=self.request.user,
            review_id=self.kwargs["review_id"],
        )

    def perform_update(self, serializer):
        super().perform_update(serializer)
        try:
            cache.delete_pattern("*location_list*")
            cache.delete_pattern("*review_list*")
        except AttributeError:
            pass
