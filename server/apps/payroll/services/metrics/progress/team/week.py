from typing import Iterable

from apps.payroll.services.metrics.progress.user import UserProgressMetrics, calculate_user_progress_metrics
from apps.users.models import User
from .base import ProgressMetricsCalculator


class WeekMetricsCalculator(ProgressMetricsCalculator):
    def calculate_user_metrics(self, user: User) -> Iterable[UserProgressMetrics]:
        return calculate_user_progress_metrics(
            user,
            self.start,
            self.end,
            'week'
        )
