from app import calc
from django.test import SimpleTestCase


class CalculTests(SimpleTestCase):
    """Tets the calc module."""

    def test_addition(self):
        """Test that two numbers are added together."""
        result = calc.add(10, 6)
        self.assertEqual(result, 12)
