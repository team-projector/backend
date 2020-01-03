# -*- coding: utf-8 -*-

from datetime import date, timedelta

from apps.users.models import User
from apps.users.services.user.metrics.progress import provider
from apps.users.services.user.metrics.progress.week.stats import (
    UserWeekStatsProvider,
)


class UserWeekMetricsGenerator:
    """User week metrics generator."""

    def __init__(
        self,
        user: User,
        start: date,
        end: date,
    ):
        """Initializing."""
        self._user = user
        self._start = start
        self._end = end

        stats_provider = UserWeekStatsProvider(user, start, end)
        self._time_spents = stats_provider.get_time_spents()
        self._deadline_stats = stats_provider.get_deadlines_stats()
        self._efficiency_stats = stats_provider.get_efficiency_stats()
        self._payrolls_stats = stats_provider.get_payrolls_stats()

    def generate_metric(self, week) -> provider.UserProgressMetrics:
        """Generate week metrics."""
        metric = provider.UserProgressMetrics()

        metric.start = week
        metric.end = week + timedelta(weeks=1)
        metric.planned_work_hours = self._user.daily_work_hours

        self._apply_stats(week, metric)

        return metric

    def _apply_stats(  # noqa: WPS211
        self,
        week: date,
        metric: provider.UserProgressMetrics,
    ) -> None:
        deadline = self._deadline_stats.get(week)
        if deadline:
            metric.issues_count = deadline["issues_count"]
            metric.time_estimate = deadline["total_time_estimate"]

        efficiency = self._efficiency_stats.get(week)
        if efficiency:
            metric.efficiency = efficiency["avg_efficiency"]

        payrolls = self._payrolls_stats.get(week)
        if payrolls:
            metric.payroll = payrolls["total_payroll"]
            metric.paid = payrolls["total_paid"]

        time_spent = self._time_spents.get(week)
        if time_spent:
            metric.time_spent = time_spent["period_spent"]
