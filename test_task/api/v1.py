from django.urls import path

from test_task.locations.api.v1.views import (
    LocationListCreateAPIView,
    LocationDetailAPIView,
)

app_name = "v1"
urlpatterns = [
    path("locations/", LocationListCreateAPIView.as_view(), name="location_list"),
    path("locations/", LocationDetailAPIView.as_view(), name="location_detail"),
]
