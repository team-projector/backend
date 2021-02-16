from datetime import date
from typing import List

from apps.development.models import Team
from apps.development.services.team.metrics.progress.base import (
    ProgressMetricsProvider,
    TeamMemberProgressMetrics,
)
from apps.development.services.team.metrics.progress.day import (
    DayMetricsProvider,
)
from apps.development.services.team.metrics.progress.week import (
    WeekMetricsProvider,
)
from apps.users.logic.services.user.progress.main import GroupProgressMetrics


def create_provider(
    team: Team,
    start: date,
    end: date,
    group: GroupProgressMetrics,
) -> ProgressMetricsProvider:
    """Create progress metrics provider."""
    if group == GroupProgressMetrics.DAY:
        return DayMetricsProvider(team, start, end)
    elif group == GroupProgressMetrics.WEEK:
        return WeekMetricsProvider(team, start, end)

    raise ValueError("Bad group '{0}'".format(group))


TeamMemberProgressMetricsList = List[TeamMemberProgressMetrics]


def get_progress_metrics(
    team: Team,
    start: date,
    end: date,
    grp: GroupProgressMetrics,
) -> TeamMemberProgressMetricsList:
    """Get progress metrics for team member."""
    provider = create_provider(team, start, end, grp)
    return provider.get_metrics()
