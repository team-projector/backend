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


def calculate_team_progress_metrics(team: Team,
                                    start: date,
                                    end: date,
                                    group: str) -> Iterable[TeamMemberProgressMetrics]:
    calculator = create_progress_calculator(team, start, end, group)
    return calculator.calculate()
