# -*- coding: utf-8 -*-

from typing import Any

from django.db import models
from django.db.models import Case, F, FloatField, Q, QuerySet, Sum, When
from django.db.models.functions import Coalesce
from django.db.models.manager import BaseManager

from apps.payroll.services.allowed.spent_time import filter_allowed_for_user


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
        from apps.development.models import issue
        from apps.development.models.merge_request import MERGE_REQUESTS_STATES

        return self.aggregate(
            total_issues=self._sum(issues__isnull=False),
            opened_issues=self._sum(issues__state=issue.ISSUE_STATES.opened),
            closed_issues=self._sum(issues__state=issue.ISSUE_STATES.closed),

            total_merges=self._sum(
                mergerequests__isnull=False,
            ),
            opened_merges=self._sum(
                mergerequests__state=MERGE_REQUESTS_STATES.opened,
            ),
            closed_merges=self._sum(
                mergerequests__state=MERGE_REQUESTS_STATES.closed,
            ),
            merged_merges=self._sum(
                mergerequests__state=MERGE_REQUESTS_STATES.merged,
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
                        salary__isnull=False, then=F('sum'),
                    ),
                    default=0,
                    output_field=FloatField(),
                ),
            )

        if payroll:
            queryset = queryset.annotate(
                payroll=Case(
                    When(
                        salary__isnull=True, then=F('sum'),
                    ),
                    default=0,
                    output_field=FloatField(),
                ),
            )

        return queryset

    @staticmethod
    def _sum(**filters) -> Coalesce:
        return Coalesce(Sum('time_spent', filter=Q(**filters)), 0)


BaseSpentTimeManager: Any = BaseManager.from_queryset(SpentTimeQuerySet)


class SpentTimeManager(BaseSpentTimeManager):
    """The Spent Time model manager."""

    def allowed_for_user(self, user):
        """Get user spent times for current user, team leader or watcher."""
        return filter_allowed_for_user(self, user)
