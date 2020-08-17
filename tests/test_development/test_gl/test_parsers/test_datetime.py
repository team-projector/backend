# -*- coding: utf-8 -*-

from datetime import datetime

from django.utils.timezone import make_aware

from apps.core.gitlab.parsers import parse_gl_datetime


def test_success():
    """Test success."""
    gl_datetime = "2000-01-01T12:00:00.000000Z"

    assert parse_gl_datetime(gl_datetime) == make_aware(
        datetime(2000, 1, 1, 12),
    )


def test_empty():
    """Test empty."""
    assert parse_gl_datetime("") is None
