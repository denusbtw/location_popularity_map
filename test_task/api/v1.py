from django.urls import path

from test_task.locations.api.v1.views import (
    LocationListCreateAPIView,
    LocationDetailAPIView,
)
from test_task.reviews.api.v1.views import (
    ReviewListCreateAPIView,
    ReviewDetailAPIView,
    ReviewVoteCreateAPIView,
    ReviewVoteDetailAPIView,
)

app_name = "v1"
urlpatterns = [
    path("locations/", LocationListCreateAPIView.as_view(), name="location_list"),
    path("locations/", LocationDetailAPIView.as_view(), name="location_detail"),
    path(
        "locations/<uuid:location_id>/reviews/",
        ReviewListCreateAPIView.as_view(),
        name="review_list",
    ),
    path(
        "locations/<uuid:location_id>/reviews/<uuid:pk>/",
        ReviewDetailAPIView.as_view(),
        name="review_detail",
    ),
    path(
        "reviews/<uuid:review_id>/votes/",
        ReviewVoteCreateAPIView.as_view(),
        name="review_vote_create",
    ),
    path(
        "reviews/<uuid:review_id>/votes/<int:pk>/",
        ReviewVoteDetailAPIView.as_view(),
        name="review_vote_detail",
    ),
]
