from datetime import date
from typing import Dict

from django.db import models
from django.db.models.functions import Cast, Coalesce, TruncDate
from django.utils.timezone import make_aware
from jnt_django_toolbox.helpers.date import date2datetime

from apps.core.models.query import TruncWeek
from apps.development.models.issue import Issue, IssueState
from apps.payroll.models import SpentTime
from apps.payroll.services.spent_time.summary import (
    spent_time_aggregation_service,
)
from apps.users.models import User

GROUP_STATS_WEEK = "week"


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

    def get_time_spents(self) -> Dict[date, Dict[str, int]]:
        """Get user time spents."""
        queryset = (
            SpentTime.objects.annotate(week=TruncWeek("date"))  # noqa: WPS221
            .filter(
                user=self._user,
                date__range=(self._start, self._end),
                week__isnull=False,
            )
            .values(GROUP_STATS_WEEK)
            .annotate(period_spent=models.Sum("time_spent"))
            .order_by()
        )

        return {stats[GROUP_STATS_WEEK]: stats for stats in queryset}

    def get_deadlines_stats(self) -> Dict[date, Dict[str, int]]:
        """Get user deadlines."""
        queryset = (
            Issue.objects.annotate(week=TruncWeek("due_date"))  # noqa: WPS221
            .filter(
                user=self._user,
                due_date__gte=self._start,
                due_date__lt=self._end,
                week__isnull=False,
            )
            .values(GROUP_STATS_WEEK)
            .annotate(
                issues_count=models.Count("*"),
                total_time_estimate=Coalesce(models.Sum("time_estimate"), 0),
            )
            .order_by()
        )

        return {stats[GROUP_STATS_WEEK]: stats for stats in queryset}

    def get_efficiency_stats(self) -> Dict[date, Dict[str, float]]:
        """Get user efficiency."""
        queryset = (
            Issue.objects.annotate(
                week=TruncWeek(TruncDate("closed_at")),
            )  # noqa: WPS221, E501
            .filter(
                user=self._user,
                closed_at__range=(
                    make_aware(date2datetime(self._start)),
                    make_aware(date2datetime(self._end)),
                ),
                state=IssueState.CLOSED,
                total_time_spent__gt=0,
                time_estimate__gt=0,
                week__isnull=False,
            )
            .values(GROUP_STATS_WEEK)
            .annotate(
                avg_efficiency=Coalesce(
                    Cast(
                        models.Sum(models.F("time_estimate")),
                        models.FloatField(),
                    )
                    / Cast(
                        models.Sum(models.F("total_time_spent")),
                        models.FloatField(),
                    ),
                    0,
                ),
            )
            .order_by()
        )

        return {stats[GROUP_STATS_WEEK]: stats for stats in queryset}

    def get_payrolls_stats(self) -> Dict[date, Dict[str, float]]:
        """Get user payrolls."""
        queryset = spent_time_aggregation_service.annotate_payrolls(
            SpentTime.objects.annotate(week=TruncWeek("date")),
        )

        queryset = (
            queryset.filter(
                user=self._user,
                date__range=(self._start, self._end),
                week__isnull=False,
            )
            .values(GROUP_STATS_WEEK)
            .annotate(
                total_payroll=Coalesce(models.Sum("sum"), 0),
                total_paid=Coalesce(models.Sum("paid"), 0),
            )
            .order_by()
        )

        return {stats[GROUP_STATS_WEEK]: stats for stats in queryset}
