# -*- coding: utf-8 -*-

from datetime import date
from typing import Dict

from django.db import models
from django.db.models import Case, Count, IntegerField, Sum, Value, When
from django.db.models.functions import Coalesce, TruncDay

from apps.development.models.issue import ISSUE_STATES, Issue
from apps.payroll.models import SpentTime
from apps.users.models import User


class UserDayStatsProvider:
    """User per day stats provider."""

    def get_time_spents(
        self,
        user: User,
        start: date,
        end: date,
    ) -> Dict[date, Dict[str, int]]:
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

    def get_due_day_stats(self, user: User) -> Dict[date, Dict[str, int]]:
        """Get user due days."""
        queryset = Issue.objects.annotate(
            due_date_truncated=TruncDay('due_date'),
            time_remains=Case(
                When(
                    models.Q(
                        time_estimate__gt=models.F('total_time_spent'),
                    ) & ~models.Q(state=ISSUE_STATES.CLOSED),
                    then=(
                        models.F('time_estimate') - models.F('total_time_spent')
                    ),
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

    def get_payrolls_stats(self, user: User) -> Dict[date, Dict[str, int]]:
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
