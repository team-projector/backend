# -*- coding: utf-8 -*-

from datetime import date
from typing import List, Optional

from apps.users.models import User


class UserProgressMetrics:
    """User progress metrics."""

    start: Optional[date] = None
    end: Optional[date] = None
    time_spent: int = 0
    time_estimate: int = 0
    time_remains: int = 0
    loading: int = 0
    efficiency: float = 0
    issues_count: int = 0
    payroll: float = 0
    paid: float = 0
    planned_work_hours: int = 0


UserProgressMetricsList = List[UserProgressMetrics]


class ProgressMetricsProvider:
    """User progress metrics provider."""

    def __init__(
        self, user: User, start: date, end: date,
    ):
        """Initialize self."""
        self.user = user
        self.start = start
        self.end = end

    def get_metrics(self) -> List[UserProgressMetrics]:
        """Method should be implemented in subclass."""
        raise NotImplementedError
