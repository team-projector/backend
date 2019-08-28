from django.db.models import QuerySet

from apps.development.models import Milestone
from ..provider import (
    IssuesContainerMetrics, IssuesContainerMetricsProvider,
    MergeRequestsContainerMetrics, MergeRequestsContainerMetricsProvider
)


class MilestoneMetrics:
    issues = IssuesContainerMetrics
    merge_requests = MergeRequestsContainerMetrics
    budget: float = 0
    budget_spent: float = 0
    budget_remains: float = 0
    profit: float = 0


class MilestoneMetricsProvider(IssuesContainerMetricsProvider,
                               MergeRequestsContainerMetricsProvider):
    def __init__(self, milestone: Milestone):
        self.milestone = milestone

    def filter_issues(self, queryset: QuerySet) -> QuerySet:
        return queryset.filter(milestone=self.milestone)

    def filter_merge_requests(self, queryset: QuerySet) -> QuerySet:
        return queryset.filter(milestone=self.milestone)

    def get_metrics(self) -> MilestoneMetrics:
        issues_metrics = IssuesContainerMetrics()
        self.fill_issues_metrics(issues_metrics)

        merge_requests_metrics = MergeRequestsContainerMetrics()
        self.fill_merge_requests_metrics(merge_requests_metrics)

        metrics = MilestoneMetrics()
        metrics.issues = issues_metrics
        metrics.merge_requests = merge_requests_metrics

        metrics.budget = self.milestone.budget
        metrics.budget_spent = metrics.issues.budget_spent + \
                               metrics.merge_requests.budget_spent

        if metrics.budget:
            metrics.budget_remains = metrics.budget - metrics.budget_spent
            metrics.profit = metrics.budget - \
                             metrics.issues.payroll - \
                             metrics.merge_requests.payroll

        return metrics
