"""User API Views."""

from rest_framework import generics

from .serializers import UserSerializer


class UserCreateAPIView(generics.CreateAPIView):
    """Create a new user."""

    serializer_class = UserSerializer
