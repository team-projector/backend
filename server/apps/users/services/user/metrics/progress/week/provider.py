from datetime import date, timedelta
from typing import List

from jnt_django_toolbox.helpers.date import begin_of_week

from apps.users.services.user.metrics.progress import provider
from apps.users.services.user.metrics.progress.week.metrics import (
    UserWeekMetricsGenerator,
)

WEEK_STEP = timedelta(weeks=1)


class WeekMetricsProvider(provider.ProgressMetricsProvider):
    """Week metrics provider."""

    def get_metrics(self) -> provider.UserProgressMetricsList:
        """Calculate and return metrics."""
        generator = UserWeekMetricsGenerator(self.user, self.start, self.end)

        return [generator.generate_metric(week) for week in self._get_weeks()]

    def _get_weeks(self) -> List[date]:
        """
        Get weeks.

        :rtype: List[date]
        """
        weeks: List[date] = []

        current = self.start
        while current <= self.end:
            weeks.append(begin_of_week(current))
            current += WEEK_STEP

        return weeks
