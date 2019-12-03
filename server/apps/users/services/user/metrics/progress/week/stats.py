# -*- coding: utf-8 -*-

from datetime import date

from django.db.models import Count, F, FloatField, Sum
from django.db.models.functions import Cast, Coalesce, TruncDate, TruncWeek
from django.utils.timezone import make_aware

from apps.core.utils.date import date2datetime
from apps.development.models.issue import ISSUE_STATES, Issue
from apps.payroll.models import SpentTime
from apps.users.models import User


class UserWeekStatsProvider:
    """User per week stats."""

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
            state=ISSUE_STATES.CLOSED,
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
