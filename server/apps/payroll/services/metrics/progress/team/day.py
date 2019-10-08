# -*- coding: utf-8 -*-

from typing import Iterable

from apps.payroll.services.metrics.progress.user import (
    UserProgressMetrics,
    get_user_progress_metrics,
)
from apps.users.models import User

from .base import ProgressMetricsProvider


class DayMetricsProvider(ProgressMetricsProvider):
    """Day metrics provider."""

    def get_user_metrics(self, user: User) -> Iterable[UserProgressMetrics]:
        """Get user progress metrics."""
        return get_user_progress_metrics(
            user,
            self.start,
            self.end,
            'day',
        )
