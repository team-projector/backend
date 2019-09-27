# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta


def date2datetime(value: date) -> datetime:
    return datetime.combine(value, datetime.min.time())


def next_weekday(value: date, weekday: int) -> date:
    days_ahead = weekday - value.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7

    return value + timedelta(days_ahead)


def begin_of_week(value: date) -> date:
    return value - timedelta(days=value.weekday() % 7)
