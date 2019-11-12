# -*- coding: utf-8 -*-

from datetime import date

from apps.users.models import User
from apps.users.services.user.metrics.progress.day.provider import (
    DayMetricsProvider,
)
from apps.users.services.user.metrics.progress.provider import (
    ProgressMetricsProvider,
    UserProgressMetricsList,
)
from apps.users.services.user.metrics.progress.week.provider import (
    WeekMetricsProvider,
)


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

    raise ValueError('Bad group "{0}"'.format(group))


def get_progress_metrics(
    user: User,
    start: date,
    end: date,
    grp: str,
) -> UserProgressMetricsList:
    """Get user progress."""
    provider = _create_provider(user, start, end, grp)
    return provider.get_metrics()
