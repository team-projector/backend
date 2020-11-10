import calendar
from datetime import date, timedelta
from typing import List

from constance import config
from jnt_django_toolbox.helpers.date import begin_of_week

from apps.users.services.user.metrics.progress import provider
from apps.users.services.user.metrics.progress.week.metrics import (
    UserWeekMetricsGenerator,
)

WEEK_STEP = timedelta(weeks=1)
WEEK_DAY_MAP = {  # noqa: WPS407
    0: calendar.SUNDAY,
    1: calendar.MONDAY,
}


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

        first_day = self._get_first_week_day()
        current = self.start
        while current <= self.end:
            weeks.append(begin_of_week(current, first_day))
            current += WEEK_STEP

        return weeks

    def _get_first_week_day(self) -> int:
        """Return number of day from calendar."""
        return WEEK_DAY_MAP.get(config.FIRST_WEEK_DAY)
