# -*- coding: utf-8 -*-

from django.db.models import Q, QuerySet, Sum
from django.db.models.functions import Coalesce

from apps.development.models import Milestone
from apps.payroll.models import SpentTime

from ..provider import IssuesContainerMetrics, IssuesContainerMetricsProvider


class MilestoneMetrics(IssuesContainerMetrics):
    """
    Milestone metrics.
    """
    budget: float = 0
    budget_spent: float = 0
    budget_remains: float = 0
    payroll: float = 0.0
    profit: float = 0


class MilestoneMetricsProvider(IssuesContainerMetricsProvider):
    """
    Milestone metrics provider.
    """
    def __init__(self, milestone: Milestone):
        self.milestone = milestone

    def filter_issues(self, queryset: QuerySet) -> QuerySet:
        """
        Filter issues.
        """
        return queryset.filter(milestone=self.milestone)

    def get_metrics(self) -> MilestoneMetrics:
        """
        Calculate and return metrics.
        """
        metrics = MilestoneMetrics()

        self.fill_issues_metrics(metrics)
        self._fill_payroll_metrics(metrics)
        metrics.budget = self.milestone.budget

        if metrics.budget:
            metrics.profit = metrics.budget - metrics.payroll
            metrics.budget_remains = metrics.budget - metrics.budget_spent

        return metrics

    def _fill_payroll_metrics(self, metrics: MilestoneMetrics) -> None:
        payroll = SpentTime.objects.filter(
            Q(issues__milestone=self.milestone)
            | Q(mergerequests__milestone=self.milestone),
        ).aggregate(
            total_sum=Coalesce(Sum('sum'), 0),
            total_customer_sum=Coalesce(Sum('customer_sum'), 0),
        )

        metrics.payroll = payroll['total_sum']
        metrics.budget_spent = payroll['total_customer_sum']
