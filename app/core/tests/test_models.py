"""Tests models."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.crypto import get_random_string


class ModelsTests(TestCase):
    """Test our models"""

    def test_create_user_with_email_successful(self):
        """Test user created with email is successful."""
        email = "test@example.com"
        password = "passer123"
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        test_emails = [
            ["testemail1@Example.com", "testemail1@example.com"],
            ["Testemail2@EXampLe.com", "Testemail2@example.com"],
            ["TESTEMAIL3@EXAMPLE.com", "TESTEMAIL3@example.com"],
            ["testemail4@example.COM", "testemail4@example.com"],
        ]
        for email, normalized in test_emails:
            user = get_user_model().objects.create_user(email, get_random_string(7))
            self.assertEqual(user.email, normalized)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", get_random_string(7))

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            email="test@example.com", password="passer123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
