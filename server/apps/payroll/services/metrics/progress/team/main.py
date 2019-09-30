# -*- coding: utf-8 -*-

from datetime import date
from typing import Iterable

from apps.development.models import Team

from .base import ProgressMetricsProvider, TeamMemberProgressMetrics
from .day import DayMetricsProvider
from .week import WeekMetricsProvider


def create_provider(
    team: Team,
    start: date,
    end: date,
    group: str,
) -> ProgressMetricsProvider:
    if group == 'day':
        return DayMetricsProvider(team, start, end)
    elif group == 'week':
        return WeekMetricsProvider(team, start, end)

    raise ValueError(f'Bad group "{group}"')


TeamMemberProgressMetricsList = Iterable[TeamMemberProgressMetrics]


def get_team_progress_metrics(
    team: Team,
    start: date,
    end: date,
    grp: str,
) -> TeamMemberProgressMetricsList:
    provider = create_provider(team, start, end, grp)
    return provider.get_metrics()
