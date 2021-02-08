from datetime import date
from enum import Enum

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


class GroupProgressMetrics(Enum):
    """Grouping progress metrics."""

    DAY = "day"  # noqa: WPS115
    WEEK = "week"  # noqa: WPS115


def _create_provider(
    user: User,
    start: date,
    end: date,
    group: GroupProgressMetrics,
) -> ProgressMetricsProvider:
    """
    Create provider.

    :param user:
    :type user: User
    :param start:
    :type start: date
    :param end:
    :type end: date
    :param group:
    :type group: str
    :rtype: ProgressMetricsProvider
    """
    if group == GroupProgressMetrics.DAY:
        return DayMetricsProvider(user, start, end)
    elif group == GroupProgressMetrics.WEEK:
        return WeekMetricsProvider(user, start, end)

    raise ValueError("Bad group '{0}'".format(group))


def get_progress_metrics(
    user: User,
    start: date,
    end: date,
    grp: GroupProgressMetrics,
) -> UserProgressMetricsList:
    """Get user progress."""
    provider = _create_provider(user, start, end, grp)
    return provider.get_metrics()
