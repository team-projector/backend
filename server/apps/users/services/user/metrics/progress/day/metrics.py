# -*- coding: utf-8 -*-


from datetime import date, datetime
from typing import Any, Dict, List

from django.conf import settings

from apps.core.utils.time import seconds
from apps.users.models import User
from apps.users.services.user.metrics.progress import provider
from apps.users.services.user.metrics.progress.day.stats import (
    UserDayStatsProvider,
)


class UserDaysMetricsGenerator:
    """User days metrics generator."""

    def __init__(
        self,
        user: User,
        start: date,
        end: date,
        active_issues: List[Dict[str, Any]],
    ):
        """Initializing."""
        self._user = user
        self._start = start
        self._end = end
        self._active_issues = active_issues
        self._now = datetime.now().date()
        self._max_day_loading = seconds(hours=self._user.daily_work_hours)

        stats = UserDayStatsProvider()
        self.time_spents = stats.get_time_spents(
            self._user,
            self._start,
            self._end,
        )
        self.due_day_stats = stats.get_due_day_stats(self._user)
        self.payrolls_stats = stats.get_payrolls_stats(self._user)

    def generate(self, current) -> provider.UserProgressMetrics:
        """Generate user metrics."""
        metric = provider.UserProgressMetrics()

        metric.start = current
        metric.end = current
        metric.planned_work_hours = self._user.daily_work_hours

        self._apply_stats(current, metric)
        self._update_loading(current, metric)

        return metric

    def replay_loading(self, current) -> None:
        """Replay user loading."""
        metric = provider.UserProgressMetrics()
        metric.start = current
        metric.end = current

        self._update_loading(current, metric)

    def _apply_stats(
        self,
        day: date,
        metric: provider.UserProgressMetrics,
    ) -> None:
        if day in self.time_spents:
            metric.time_spent = self.time_spents[day]['period_spent']

        if day in self.due_day_stats:
            progress = self.due_day_stats[day]
            metric.issues_count = progress['issues_count']
            metric.time_estimate = progress['total_time_estimate']
            metric.time_remains = progress['total_time_remains']

        if day in self.payrolls_stats:
            payrolls = self.payrolls_stats[day]
            metric.payroll = payrolls['total_payroll']
            metric.paid = payrolls['total_paid']

    def _update_loading(
        self,
        current,
        metric: provider.UserProgressMetrics,
    ) -> None:
        is_update_loading = (
            current >= self._now
            and current.weekday() not in settings.TP_WEEKENDS_DAYS
        )

        if not is_update_loading:
            return

        if not self._active_issues:
            return

        metric.loading = metric.time_spent

        self._apply_deadline_issues_loading(
            metric,
            self._active_issues,
        )

        if metric.loading > self._max_day_loading:
            return

        self._apply_active_issues_loading(
            metric,
            self._active_issues,
        )

    def _apply_deadline_issues_loading(
        self,
        metric: provider.UserProgressMetrics,
        active_issues: List[dict],
    ) -> None:
        deadline_issues = [
            issue
            for issue in active_issues
            if issue['due_date'] and issue['due_date'] <= metric.start
        ]

        for issue in deadline_issues:
            metric.loading += issue['remaining']
            active_issues.remove(issue)

    def _apply_active_issues_loading(
        self,
        metric: provider.UserProgressMetrics,
        active_issues: List[dict],
    ) -> None:
        for issue in active_issues[:]:
            available_time = self._max_day_loading - metric.loading

            loading = min(available_time, issue['remaining'])

            metric.loading += loading

            issue['remaining'] -= loading
            if not issue['remaining']:
                active_issues.remove(issue)
