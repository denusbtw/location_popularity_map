from django.urls import path, include

urlpatterns = [
    path("v1/", include("test_task.api.v1")),
]
