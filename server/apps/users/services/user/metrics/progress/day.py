# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from typing import List

from django.conf import settings
from django.db.models import Case, Count, F, IntegerField, Q, Sum, Value, When
from django.db.models.functions import Coalesce, TruncDay

from apps.development.models.issue import ISSUE_STATES, Issue
from apps.payroll.models import SpentTime
from apps.users.services.user.metrics.progress import base

DAY_STEP = timedelta(days=1)


class DayMetricsProvider(base.ProgressMetricsProvider):
    """Day metrics provider."""

    def get_metrics(self) -> base.UserProgressMetricsList:
        """Calculate and return metrics."""
        now = datetime.now().date()

        active_issues = self.get_active_issues() if now <= self.end else []

        time_spents = _get_time_spents(self.user, self.start, self.end)
        due_day_stats = _get_due_day_stats(self.user)
        payrols_stats = _get_payrolls_stats(self.user)

        if self.start > now:
            self._replay_loading(now, active_issues)

        current = self.start
        metrics = []

        while current <= self.end:
            metric = base.UserProgressMetrics()
            metrics.append(metric)

            metric.start = current
            metric.end = current
            metric.planned_work_hours = self.user.daily_work_hours

            if current in time_spents:
                metric.time_spent = time_spents[current]['period_spent']

            self._apply_stats(current, metric, due_day_stats, payrols_stats)

            if self._is_apply_loading(current, now):
                self._update_loading(metric, active_issues)

            current += DAY_STEP

        return metrics

    def _replay_loading(
        self,
        now: date,
        active_issues: List[dict],
    ) -> None:
        current = now

        while current < self.start:
            if not active_issues:
                return

            metric = base.UserProgressMetrics()
            metric.start = current
            metric.end = current

            if self._is_apply_loading(current, now):
                self._update_loading(metric, active_issues)

            current += DAY_STEP

    def _apply_stats(
        self,
        day: date,
        metric: base.UserProgressMetrics,
        due_day_stats: dict,
        payrolls_stats: dict,
    ) -> None:
        if day in due_day_stats:
            progress = due_day_stats[day]
            metric.issues_count = progress['issues_count']
            metric.time_estimate = progress['total_time_estimate']
            metric.time_remains = progress['total_time_remains']

        if day in payrolls_stats:
            payrolls = payrolls_stats[day]
            metric.payroll = payrolls['total_payroll']
            metric.paid = payrolls['total_paid']

    def _is_apply_loading(
        self,
        day: date,
        now: date,
    ) -> bool:
        return day >= now and day.weekday() not in settings.TP_WEEKENDS_DAYS

    def _update_loading(
        self,
        metric: base.UserProgressMetrics,
        active_issues: List[dict],
    ) -> None:
        if not active_issues:
            return

        metric.loading = metric.time_spent

        self._apply_deadline_issues_loading(
            metric,
            active_issues,
        )

        if metric.loading > self.max_day_loading:
            return

        self._apply_active_issues_loading(
            metric,
            active_issues,
        )

    def _apply_deadline_issues_loading(
        self,
        metric: base.UserProgressMetrics,
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
        metric: base.UserProgressMetrics,
        active_issues: List[dict],
    ) -> None:
        for issue in active_issues[:]:
            available_time = self.max_day_loading - metric.loading

            loading = min(available_time, issue['remaining'])

            metric.loading += loading

            issue['remaining'] -= loading
            if not issue['remaining']:
                active_issues.remove(issue)


def _get_time_spents(user, start, end) -> dict:
    queryset = SpentTime.objects.annotate(
        day=TruncDay('date'),
    ).filter(
        user=user,
        date__range=(start, end),
        day__isnull=False,
    ).values(
        'day',
    ).annotate(
        period_spent=Sum('time_spent'),
    ).order_by()

    return {
        stats['day']: stats
        for stats in queryset
    }


def _get_due_day_stats(user) -> dict:
    queryset = Issue.objects.annotate(
        due_date_truncated=TruncDay('due_date'),
        time_remains=Case(
            When(
                Q(time_estimate__gt=F('total_time_spent')) &  # noqa:W504
                ~Q(state=ISSUE_STATES.closed),
                then=F('time_estimate') - F('total_time_spent'),
            ),
            default=Value(0),
            output_field=IntegerField(),
        ),
    ).filter(
        user=user,
        due_date_truncated__isnull=False,
    ).values(
        'due_date_truncated',
    ).annotate(
        issues_count=Count('*'),
        total_time_estimate=Coalesce(Sum('time_estimate'), 0),
        total_time_remains=Coalesce(Sum('time_remains'), 0),
    ).order_by()

    return {
        stats['due_date_truncated']: stats
        for stats in queryset
    }


def _get_payrolls_stats(user) -> dict:
    queryset = SpentTime.objects.annotate(
        date_truncated=TruncDay('date'),
    ).annotate_payrolls()

    queryset = queryset.filter(
        user=user,
        date_truncated__isnull=False,
    ).values(
        'date_truncated',
    ).annotate(
        total_payroll=Coalesce(Sum('payroll'), 0),
        total_paid=Coalesce(Sum('paid'), 0),
    ).order_by()

    return {
        stats['date_truncated']: stats
        for stats in queryset
    }
