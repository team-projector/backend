# -*- coding: utf-8 -*-


from datetime import date
from typing import Any, Dict, List

from django.conf import settings

from apps.users.services.user.metrics.progress import provider
from apps.users.services.user.metrics.progress.day.stats import (
    UserDayStatsProvider,
)


class UserDaysMetricsGenerator:
    def __init__(
        self,
        user,
        start,
        end,
        now: date,
        max_day_loading,
        active_issues: List[Dict[str, Any]],
    ):
        self.user = user
        self.now = now
        self.start = start
        self.end = end
        self.max_day_loading = max_day_loading
        self.active_issues = active_issues

        stats = UserDayStatsProvider()
        self.time_spents = stats.get_time_spents(
            self.user,
            self.start,
            self.end,
        )
        self.due_day_stats = stats.get_due_day_stats(self.user)
        self.payrolls_stats = stats.get_payrolls_stats(self.user)

    def generate(self, current) -> provider.UserProgressMetrics:
        metric = provider.UserProgressMetrics()

        metric.start = current
        metric.end = current
        metric.planned_work_hours = self.user.daily_work_hours

        if current in self.time_spents:
            metric.time_spent = self.time_spents[current]['period_spent']

        self._apply_stats(current, metric)

        if self._is_apply_loading(current):
            self._update_loading(metric)

        return metric

    def replay_loading(self, current) -> None:
        """Replay user loading."""
        metric = provider.UserProgressMetrics()
        metric.start = current
        metric.end = current

        if self._is_apply_loading(current):
            self._update_loading(metric)

    def _apply_stats(
        self,
        day: date,
        metric: provider.UserProgressMetrics,
    ) -> None:
        if day in self.due_day_stats:
            progress = self.due_day_stats[day]
            metric.issues_count = progress['issues_count']
            metric.time_estimate = progress['total_time_estimate']
            metric.time_remains = progress['total_time_remains']

        if day in self.payrolls_stats:
            payrolls = self.payrolls_stats[day]
            metric.payroll = payrolls['total_payroll']
            metric.paid = payrolls['total_paid']

    def _is_apply_loading(
        self,
        day: date,
    ) -> bool:
        return (
            day >= self.now
            and day.weekday() not in settings.TP_WEEKENDS_DAYS
        )

    def _update_loading(
        self,
        metric: provider.UserProgressMetrics,
    ) -> None:
        if not self.active_issues:
            return

        metric.loading = metric.time_spent

        self._apply_deadline_issues_loading(
            metric,
            self.active_issues,
        )

        if metric.loading > self.max_day_loading:
            return

        self._apply_active_issues_loading(
            metric,
            self.active_issues,
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
            available_time = self.max_day_loading - metric.loading

            loading = min(available_time, issue['remaining'])

            metric.loading += loading

            issue['remaining'] -= loading
            if not issue['remaining']:
                active_issues.remove(issue)
