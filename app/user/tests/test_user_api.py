""" Tests for User API"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserAPITests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful."""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name",
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn("password", res.data)

    def test_user_exists(self):
        """Test creating user that already exists (email) fails."""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Nom",
        }

        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_password_too_short(self):
        """Test creating user with a password too short fails."""

        payload = {"email": "test@example.com", "password": "123", "name": "Test Name"}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(email=payload["email"]).exists()
        self.assertFalse(user_exists)

    def create_user_token(self):
        """Test a token is created for the user."""
        # Register
        user_info = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User Name",
        }
        create_user(**user_info)

        # Get Token
        res = self.client.post(
            TOKEN_URL, {"email": user_info["email"], "password": user_info["password"]}
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given."""
        user_info = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User Name",
        }
        create_user(**user_info)
        res = self.client.post(
            TOKEN_URL, {"email": user_info["email"], "password": "anypass"}
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)

    def test_create_token_missing_field(self):
        """Test that token creation fails if email or password is missing."""
        res = self.client.post(TOKEN_URL, {"email": "one", "password": ""})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", res.data)


class PrivateUserAPITests(TestCase):
    """Test API requests that require authentications."""

    def setUp(self):
        self.user = create_user(
            email="test@example.com", password="testpass123", name="Test Name"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user_profile(self):
        """Test retrieving profile for logged in user."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {"name": self.user.name, "email": self.user.email})

    def test_user_profile_post_not_allowed(self):
        """Test that POST is not allowed on the user profile URL."""
        res = self.client.post(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test Update User profile is successful."""
        update_data = {"name": "Updated Name", "password": "New password"}
        res = self.client.patch(ME_URL, update_data)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, update_data["name"])
        self.assertTrue(self.user.check_password(update_data["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
