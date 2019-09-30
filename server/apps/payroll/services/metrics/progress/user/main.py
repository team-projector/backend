# -*- coding: utf-8 -*-

from datetime import date
from typing import Iterable

from apps.users.models import User

from .base import ProgressMetricsProvider, UserProgressMetrics
from .day import DayMetricsProvider
from .week import WeekMetricsProvider


def _create_provider(
    user: User,
    start: date,
    end: date,
    group: str,
) -> ProgressMetricsProvider:
    if group == 'day':
        return DayMetricsProvider(user, start, end)
    elif group == 'week':
        return WeekMetricsProvider(user, start, end)

    raise ValueError(f'Bad group "{group}"')


def get_user_progress_metrics(
    user: User,
    start: date,
    end: date,
    grp: str,
) -> Iterable[UserProgressMetrics]:
    provider = _create_provider(user, start, end, grp)
    return provider.get_metrics()
