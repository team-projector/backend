from datetime import datetime

from apps.users.models import User
from .base import MetricsCalculator
from .day import DayMetricsCalculator
from .week import WeekMetricsCalculator


def create_calculator(user: User, start: datetime, end: datetime, group: str) -> MetricsCalculator:
    if group == 'day':
        return DayMetricsCalculator(user, start, end)
    elif group == 'week':
        return WeekMetricsCalculator(user, start, end)

    raise ValueError(f'Bad group "{group}"')
