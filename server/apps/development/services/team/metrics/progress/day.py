# -*- coding: utf-8 -*-

from apps.development.services.team.metrics.progress.base import (
    ProgressMetricsProvider,
    UserProgressMetricsList,
)
from apps.users.models import User
from apps.users.services import user as user_service


class DayMetricsProvider(ProgressMetricsProvider):
    """Day metrics provider."""

    def get_user_metrics(self, user: User) -> UserProgressMetricsList:
        """Get user progress metrics."""
        return user_service.get_progress_metrics(
            user,
            self.start,
            self.end,
            'day',
        )
