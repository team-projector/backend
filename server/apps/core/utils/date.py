# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta


def date2datetime(value: date) -> datetime:  # noqa: WPS110
    """Converts date to datetime."""
    return datetime.combine(value, datetime.min.time())


def begin_of_week(value: date) -> date:  # noqa: WPS110
    """Get begin of week."""
    return value - timedelta(days=value.weekday() % 7)
