# -*- coding: utf-8 -*-

from apps.development.services.team.metrics.progress.base import (
    ProgressMetricsProvider,
    UserProgressMetricsList,
)
from apps.users.models import User
from apps.users.services.user import get_progress_metrics


class WeekMetricsProvider(ProgressMetricsProvider):
    """Week metrics provider."""

    def get_user_metrics(self, user: User) -> UserProgressMetricsList:
        """Get user progress metrics."""
        return get_progress_metrics(
            user,
            self.start,
            self.end,
            'week',
        )
