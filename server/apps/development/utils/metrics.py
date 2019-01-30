from datetime import datetime
from typing import Iterable

from apps.users.models import User


class Metric:
    start = None
    end = None
    time_spent = None
    time_estimate = None
    efficiency = None
    earnings = None


class MetricsCalculator:
    def __init__(self, user: User, start: datetime, end: datetime, group: str):
        self.user = user
        self.start = start
        self.end = end
        self.group = group

    def calculate(self) -> Iterable[Metric]:
        return []
