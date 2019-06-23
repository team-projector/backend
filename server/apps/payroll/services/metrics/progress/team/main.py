from datetime import date
from typing import Iterable

from apps.development.models import Team
from .base import ProgressMetricsCalculator, TeamMemberProgressMetrics
from .day import DayMetricsCalculator
from .week import WeekMetricsCalculator


def create_progress_calculator(team: Team,
                               start: date,
                               end: date,
                               group: str) -> ProgressMetricsCalculator:
    if group == 'day':
        return DayMetricsCalculator(team, start, end)
    elif group == 'week':
        return WeekMetricsCalculator(team, start, end)

    raise ValueError(f'Bad group "{group}"')


TeamMemberProgressMetricsList = Iterable[TeamMemberProgressMetrics]


def calculate_team_progress_metrics(team: Team,
                                    start: date,
                                    end: date,
                                    grp: str) -> TeamMemberProgressMetricsList:
    calculator = create_progress_calculator(team, start, end, grp)
    return calculator.calculate()
