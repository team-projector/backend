from apps.development.services.team.metrics.progress.base import (
    ProgressMetricsProvider,
    UserProgressMetricsList,
)
from apps.users.logic.services.user.progress.main import (
    GroupProgressMetrics,
    get_progress_metrics,
)
from apps.users.models import User


class WeekMetricsProvider(ProgressMetricsProvider):
    """Week metrics provider."""

    def get_user_metrics(self, user: User) -> UserProgressMetricsList:
        """Get user progress metrics."""
        return get_progress_metrics(
            user,
            self.start,
            self.end,
            GroupProgressMetrics.WEEK,
        )
