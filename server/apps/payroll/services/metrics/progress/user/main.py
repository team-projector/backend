from datetime import date
from typing import Iterable

from apps.users.models import User
from .base import ProgressMetricsCalculator, UserProgressMetrics
from .day import DayMetricsCalculator
from .week import WeekMetricsCalculator


def create_progress_calculator(user: User,
                               start: date,
                               end: date,
                               group: str) -> ProgressMetricsCalculator:
    if group == 'day':
        return DayMetricsCalculator(user, start, end)
    elif group == 'week':
        return WeekMetricsCalculator(user, start, end)

    raise ValueError(f'Bad group "{group}"')


def calculate_user_progress_metrics(user: User,
                                    start: date,
                                    end: date,
                                    grp: str) -> Iterable[UserProgressMetrics]:
    calculator = create_progress_calculator(user, start, end, grp)
    return calculator.calculate()
