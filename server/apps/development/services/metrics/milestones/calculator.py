from django.db.models import QuerySet

from apps.development.models import Milestone
from ..calculator import IssuesContainerCalculator, IssuesContainerMetrics


class MilestoneMetrics(IssuesContainerMetrics):
    budget_remains: int = 0
    profit: int = 0


class MilestoneMetricsCalculator(IssuesContainerCalculator):
    def __init__(self, milestone: Milestone):
        self.milestone = milestone

    def filter_issues(self, queryset: QuerySet) -> QuerySet:
        return queryset.filter(milestone=self.milestone)

    def calculate(self) -> MilestoneMetrics:
        metrics = MilestoneMetrics()

        self.fill_issues_metrics(metrics)

        return metrics
