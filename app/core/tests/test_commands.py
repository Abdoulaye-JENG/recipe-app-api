"""Test custom Django management commands."""

# We want to mock the behavior of the database
# We need to be able to simulate whether the database
# is returnng a response or not
from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase
from psycopg2 import OperationalError as Psycopg2Error


@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    """Test management commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""
        patched_check.return_value = True

        # Call our `wait_for_db` management command
        call_command("wait_for_db")

        # Knowing that every management command inheriting from `BaseCommand`
        # has a `check` method which will be called to make sure everything
        # is valid;
        # So then we make sure our database is righly configured and ready
        patched_check.assert_called_once_with(databases=["default"])

    @patch("time.sleep")
    def test_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError."""
        patched_check.side_effect = (
            [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]
        )

        call_command("wait_for_db")

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=["default"])
