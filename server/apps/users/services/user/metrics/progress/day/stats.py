# -*- coding: utf-8 -*-

from datetime import date
from typing import Dict

from django.db import models
from django.db.models.functions import Coalesce, TruncDay

from apps.development.models.issue import Issue, IssueState
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
            day=TruncDay("date"),
        ).filter(
            user=user,
            date__range=(start, end),
            day__isnull=False,
        ).values(
            "day",
        ).annotate(
            period_spent=models.Sum("time_spent"),
        ).order_by()

        return {
            stats["day"]: stats
            for stats in queryset
        }

    def get_due_day_stats(self, user: User) -> Dict[date, Dict[str, int]]:
        """Get user due days."""
        queryset = Issue.objects.annotate(
            due_date_truncated=TruncDay("due_date"),
            time_remains=models.Case(
                models.When(
                    models.Q(
                        time_estimate__gt=models.F("total_time_spent"),
                    ) & ~models.Q(state=IssueState.CLOSED),
                    then=(
                        models.F("time_estimate") - models.F("total_time_spent")
                    ),
                ),
                default=models.Value(0),
                output_field=models.IntegerField(),
            ),
        ).filter(
            user=user,
            due_date_truncated__isnull=False,
        ).values(
            "due_date_truncated",
        ).annotate(
            issues_count=models.Count("*"),
            total_time_estimate=Coalesce(models.Sum("time_estimate"), 0),
            total_time_remains=Coalesce(models.Sum("time_remains"), 0),
        ).order_by()

        return {
            stats["due_date_truncated"]: stats
            for stats in queryset
        }

    def get_payrolls_stats(self, user: User) -> Dict[date, Dict[str, int]]:
        """Get user payrolls."""
        queryset = SpentTime.objects.annotate(
            date_truncated=TruncDay("date"),
        ).annotate_payrolls()

        queryset = queryset.filter(
            user=user,
            date_truncated__isnull=False,
        ).values(
            "date_truncated",
        ).annotate(
            total_payroll=Coalesce(models.Sum("payroll"), 0),
            total_paid=Coalesce(models.Sum("paid"), 0),
        ).order_by()

        return {
            stats["date_truncated"]: stats
            for stats in queryset
        }
