# -*- coding: utf-8 -*-

from datetime import date, timedelta
from typing import List

from django.db.models import Count, F, FloatField, Sum
from django.db.models.functions import Cast, Coalesce, TruncDate, TruncWeek
from django.utils.timezone import make_aware

from apps.core.utils.date import begin_of_week, date2datetime
from apps.development.models.issue import ISSUE_STATES, Issue
from apps.payroll.models import SpentTime
from apps.users.models import User
from apps.users.services.user.metrics.progress import base

WEEK_STEP = timedelta(weeks=1)


class WeekMetricsProvider(base.ProgressMetricsProvider):
    """Week metrics provider."""

    def get_metrics(self) -> base.UserProgressMetricsList:
        """Calculate and return metrics."""
        generator = _MetricsGenerator(
            self.user,
            self.start,
            self.end,
        )

        return [
            generator.generate_metric(week)
            for week in self._get_weeks()
        ]

    def _get_weeks(self) -> List[date]:
        ret: List[date] = []
        current = self.start

        while current <= self.end:
            ret.append(begin_of_week(current))
            current += WEEK_STEP

        return ret


class _MetricsGenerator:
    def __init__(
        self,
        user,
        start: date,
        end: User,
    ):
        self._user = user
        self._start = start
        self._end = end

        stats_provider = _StatsProvider(user, start, end)
        self._time_spents = stats_provider.get_time_spents()
        self._deadline_stats = stats_provider.get_deadlines_stats()
        self._efficiency_stats = stats_provider.get_efficiency_stats()
        self._payrolls_stats = stats_provider.get_payrolls_stats()

    def generate_metric(self, week) -> base.UserProgressMetrics:
        metric = base.UserProgressMetrics()

        metric.start = week
        metric.end = week + timedelta(weeks=1)
        metric.planned_work_hours = self._user.daily_work_hours

        self._apply_stats(
            week,
            metric,
        )

        return metric

    def _apply_stats(  # noqa WPS211
        self,
        week: date,
        metric: base.UserProgressMetrics,
    ) -> None:
        if week in self._deadline_stats:
            deadline = self._deadline_stats[week]
            metric.issues_count = deadline['issues_count']
            metric.time_estimate = deadline['total_time_estimate']

        if week in self._efficiency_stats:
            efficiency = self._efficiency_stats[week]
            metric.efficiency = efficiency['avg_efficiency']

        if week in self._payrolls_stats:
            payrolls = self._payrolls_stats[week]
            metric.payroll = payrolls['total_payroll']
            metric.paid = payrolls['total_paid']

        if week in self._time_spents:
            spent = self._time_spents[week]
            metric.time_spent = spent['period_spent']


class _StatsProvider:
    def __init__(self, user, start, end):
        """Initializing."""
        self._user = user
        self._start = start
        self._end = end

    def get_time_spents(self) -> dict:
        """Get user time spents."""
        queryset = SpentTime.objects.annotate(
            week=TruncWeek('date'),
        ).filter(
            user=self._user,
            date__range=(self._start, self._end),
            week__isnull=False,
        ).values(
            'week',
        ).annotate(
            period_spent=Sum('time_spent'),
        ).order_by()

        return {
            stats['week']: stats
            for stats in queryset
        }

    def get_deadlines_stats(self) -> dict:
        """Get user deadlines."""
        queryset = Issue.objects.annotate(
            week=TruncWeek('due_date'),
        ).filter(
            user=self._user,
            due_date__gte=self._start,
            due_date__lt=self._end,
            week__isnull=False,
        ).values(
            'week',
        ).annotate(
            issues_count=Count('*'),
            total_time_estimate=Coalesce(Sum('time_estimate'), 0),
        ).order_by()

        return {
            stats['week']: stats
            for stats in queryset
        }

    def get_efficiency_stats(self) -> dict:
        """Get user efficiency."""
        queryset = Issue.objects.annotate(
            week=TruncWeek(TruncDate('closed_at')),
        ).filter(
            user=self._user,
            closed_at__range=(
                make_aware(date2datetime(self._start)),
                make_aware(date2datetime(self._end)),
            ),
            state=ISSUE_STATES.closed,
            total_time_spent__gt=0,
            time_estimate__gt=0,
            week__isnull=False,
        ).values(
            'week',
        ).annotate(
            avg_efficiency=Coalesce(
                Cast(Sum(F('time_estimate')), FloatField()) /  # noqa:W504
                Cast(Sum(F('total_time_spent')), FloatField()),
                0,
            ),
        ).order_by()

        return {
            stats['week']: stats
            for stats in queryset
        }

    def get_payrolls_stats(self) -> dict:
        """Get user payrolls."""
        queryset = SpentTime.objects.annotate(
            week=TruncWeek('date'),
        ).annotate_payrolls()

        queryset = queryset.filter(
            user=self._user,
            date__range=(self._start, self._end),
            week__isnull=False,
        ).values(
            'week',
        ).annotate(
            total_payroll=Coalesce(Sum('payroll'), 0),
            total_paid=Coalesce(Sum('paid'), 0),
        ).order_by()

        return {
            stats['week']: stats
            for stats in queryset
        }
