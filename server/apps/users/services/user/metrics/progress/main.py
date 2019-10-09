# -*- coding: utf-8 -*-

from datetime import date

from apps.users.models import User
from apps.users.services.user.metrics.progress.base import (
    ProgressMetricsProvider,
    UserProgressMetricsList,
)
from apps.users.services.user.metrics.progress.day import DayMetricsProvider
from apps.users.services.user.metrics.progress.week import WeekMetricsProvider


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


def get_progress_metrics(
    user: User,
    start: date,
    end: date,
    grp: str,
) -> UserProgressMetricsList:
    """Get user progress."""
    provider = _create_provider(user, start, end, grp)
    return provider.get_metrics()
