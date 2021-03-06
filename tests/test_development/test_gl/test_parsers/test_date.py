from datetime import date

from apps.core.gitlab.parsers import parse_gl_date


def test_empty():
    """Test empty."""
    assert parse_gl_date("") is None


def test_success():
    """Test success."""
    assert parse_gl_date("2000-01-01") == date(2000, 1, 1)
