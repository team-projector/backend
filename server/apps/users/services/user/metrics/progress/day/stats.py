# -*- coding: utf-8 -*-

from django.db.models import Case, Count, F, IntegerField, Q, Sum, Value, When
from django.db.models.functions import Coalesce, TruncDay

from apps.development.models.issue import ISSUE_STATES, Issue
from apps.payroll.models import SpentTime


class UserDayStatsProvider:
    """User per day stats provider."""

    def get_time_spents(
        self,
        user,
        start,
        end,
    ) -> dict:
        """Get user time spents in range."""
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

    def get_due_day_stats(self, user) -> dict:
        """Get user due days."""
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

    def get_payrolls_stats(self, user) -> dict:
        """Get user payrolls."""
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
