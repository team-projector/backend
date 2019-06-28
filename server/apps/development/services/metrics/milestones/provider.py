from django.db.models import QuerySet

from apps.development.models import Milestone
from ..provider import IssuesContainerMetricsProvider, IssuesContainerMetrics


class MilestoneMetrics(IssuesContainerMetrics):
    budget: float = 0
    budget_remains: float = 0
    profit: float = 0


class MilestoneMetricsProvider(IssuesContainerMetricsProvider):
    def __init__(self, milestone: Milestone):
        self.milestone = milestone

    def filter_issues(self, queryset: QuerySet) -> QuerySet:
        return queryset.filter(milestone=self.milestone)

    def get_metrics(self) -> MilestoneMetrics:
        metrics = MilestoneMetrics()

        self.fill_issues_metrics(metrics)
        metrics.budget = self.milestone.budget

        if metrics.budget:
            metrics.profit = metrics.budget - metrics.payroll
            metrics.budget_remains = metrics.budget - metrics.customer_payroll

        return metrics
