import pytest


def test_always_fails():
    """Test function designed to fail."""
    pytest.fail("This test is intentionally designed to fail")
