# -*- coding: utf-8 -*-

from datetime import date, datetime
from typing import Dict, List

from constance import config
from jnt_django_toolbox.helpers.time import seconds

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
        active_issues: List[Dict[str, object]],
    ):
        """Initializing."""
        self._user = user
        self._start = start
        self._end = end
        self._active_issues = active_issues
        self._now = datetime.now().date()
        self._max_day_loading = seconds(hours=self._user.daily_work_hours)

        stats = UserDayStatsProvider()
        self._time_spents = stats.get_time_spents(
            self._user, self._start, self._end,
        )
        self._due_day_stats = stats.get_due_day_stats(self._user)
        self._payrolls_stats = stats.get_payrolls_stats(self._user)

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
        self, day: date, metric: provider.UserProgressMetrics,
    ) -> None:
        """
        Apply stats.

        :param day:
        :type day: date
        :param metric:
        :type metric: provider.UserProgressMetrics
        :rtype: None
        """
        time_spent = self._time_spents.get(day)
        if time_spent:
            metric.time_spent = time_spent["period_spent"]

        due_day_stats = self._due_day_stats.get(day)
        if due_day_stats:
            metric.issues_count = due_day_stats["issues_count"]
            metric.time_estimate = due_day_stats["total_time_estimate"]
            metric.time_remains = due_day_stats["total_time_remains"]

        payrolls = self._payrolls_stats.get(day)
        if payrolls:
            metric.payroll = payrolls["total_payroll"]
            metric.paid = payrolls["total_paid"]

    def _update_loading(
        self, current, metric: provider.UserProgressMetrics,
    ) -> None:
        """
        Update loading.

        :param current:
        :param metric:
        :type metric: provider.UserProgressMetrics
        :rtype: None
        """
        is_update_loading = (
            current >= self._now
            and current.weekday() not in config.WEEKENDS_DAYS
        )

        if not is_update_loading:
            return

        if not self._active_issues:
            return

        metric.loading = metric.time_spent

        self._apply_deadline_issues_loading(
            metric, self._active_issues,
        )

        if metric.loading > self._max_day_loading:
            return

        self._apply_active_issues_loading(
            metric, self._active_issues,
        )

    def _apply_deadline_issues_loading(
        self,
        metric: provider.UserProgressMetrics,
        active_issues: List[Dict[str, object]],
    ) -> None:
        """
        Apply deadline issues loading.

        :param metric:
        :type metric: provider.UserProgressMetrics
        :param active_issues:
        :type active_issues: List[Dict]
        :rtype: None
        """
        deadline_issues = [
            issue
            for issue in active_issues
            if issue["due_date"] and issue["due_date"] <= metric.start
        ]

        for issue in deadline_issues:
            metric.loading += issue["remaining"]
            active_issues.remove(issue)

    def _apply_active_issues_loading(
        self,
        metric: provider.UserProgressMetrics,
        active_issues: List[Dict[str, object]],
    ) -> None:
        """
        Apply active issues loading.

        :param metric:
        :type metric: provider.UserProgressMetrics
        :param active_issues:
        :type active_issues: List[Dict]
        :rtype: None
        """
        for issue in active_issues[:]:
            available_time = self._max_day_loading - metric.loading

            loading = min(available_time, issue["remaining"])

            metric.loading += loading

            issue["remaining"] -= loading
            if not issue["remaining"]:
                active_issues.remove(issue)
