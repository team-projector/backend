from datetime import date

from apps.users.models import User
from .base import ProgressMetricsCalculator
from .day import DayMetricsCalculator
from .week import WeekMetricsCalculator


def create_progress_calculator(user: User, start: date, end: date, group: str) -> ProgressMetricsCalculator:
    if group == 'day':
        return DayMetricsCalculator(user, start, end)
    elif group == 'week':
        return WeekMetricsCalculator(user, start, end)

    raise ValueError(f'Bad group "{group}"')
