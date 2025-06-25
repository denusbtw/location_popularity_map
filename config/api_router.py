from django.urls import path, include

urlpatterns = [
    path("v1/auth/", include("dj_rest_auth.urls")),
    path("v1/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("v1/", include("test_task.api.v1")),
]

from dj_rest_auth.views import PasswordResetConfirmView

urlpatterns += [
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
