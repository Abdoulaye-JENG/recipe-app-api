"""URL mapping for User API."""

from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    path("create/", views.UserCreateAPIView.as_view(), name="create"),
    path("token/", views.CreateTokenAPIView.as_view(), name="token"),
    path("me/", views.UserProfileAPIView.as_view(), name="me"),
]
