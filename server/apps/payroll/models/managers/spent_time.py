# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Case, FloatField, QuerySet, Sum, When
from django.db.models.functions import Coalesce
from django.db.models.manager import BaseManager


class SpentTimeQuerySet(models.QuerySet):
    """Spent Time QuerySet."""

    def aggregate_payrolls(self):
        """Get total sum payroll and paid."""
        return self.annotate_payrolls().aggregate(
            total_payroll=Coalesce(Sum('payroll'), 0),
            total_paid=Coalesce(Sum('paid'), 0),
        )

    def summaries(self):
        """Get spent time summaries."""
        from apps.development.models import issue  # noqa: WPS433
        from apps.development.models.merge_request import (  # noqa: WPS433
            MERGE_REQUESTS_STATES,
        )

        return self.aggregate(
            total_issues=self._sum(issues__isnull=False),
            opened_issues=self._sum(issues__state=issue.ISSUE_STATES.OPENED),
            closed_issues=self._sum(issues__state=issue.ISSUE_STATES.CLOSED),

            total_merges=self._sum(
                mergerequests__isnull=False,
            ),
            opened_merges=self._sum(
                mergerequests__state=MERGE_REQUESTS_STATES.OPENED,
            ),
            closed_merges=self._sum(
                mergerequests__state=MERGE_REQUESTS_STATES.CLOSED,
            ),
            merged_merges=self._sum(
                mergerequests__state=MERGE_REQUESTS_STATES.MERGED,
            ),
        )

    def annotate_payrolls(
        self,
        paid: bool = True,
        payroll: bool = True,
    ) -> QuerySet:
        """Get total sum payroll or paid."""
        queryset = self

        if paid:
            queryset = queryset.annotate(
                paid=Case(
                    When(
                        salary__isnull=False, then=models.F('sum'),
                    ),
                    default=0,
                    output_field=FloatField(),
                ),
            )

        if payroll:
            queryset = queryset.annotate(
                payroll=Case(
                    When(
                        salary__isnull=True, then=models.F('sum'),
                    ),
                    default=0,
                    output_field=FloatField(),
                ),
            )

        return queryset

    def _sum(self, **filters) -> Coalesce:
        return Coalesce(Sum('time_spent', filter=models.Q(**filters)), 0)


BaseSpentTimeManager: type = BaseManager.from_queryset(SpentTimeQuerySet)


class SpentTimeManager(BaseSpentTimeManager):  # type: ignore
    """The Spent Time model manager."""

    def allowed_for_user(self, user):
        """Get user spent times for current user, team leader or watcher."""
        from apps.payroll.services.spent_time.allowed import (  # noqa: WPS433
            filter_allowed_for_user,
        )
        return filter_allowed_for_user(self, user)
