# -*- coding: utf-8 -*-

from apps.users.models import User
from apps.users.services import user as user_service

from .base import ProgressMetricsProvider, UserProgressMetricsList


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
