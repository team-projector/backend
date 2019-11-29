# -*- coding: utf-8 -*-

from django.db.models import Count, Q, QuerySet, Sum
from django.db.models.functions import Coalesce

from apps.development.models import Issue
from apps.development.models.issue import ISSUE_STATES
from apps.payroll.models import SpentTime


class IssueMetrics:
    """Issue metrics."""

    remains: int = 0
    efficiency: float = 0
    payroll: float = 0
    paid: float = 0


def get_metrics(issue: Issue) -> IssueMetrics:
    """Get metrics for issue."""
    payroll = SpentTime.objects.filter(
        issues__id=issue.id,
    ).aggregate_payrolls()

    metrics = IssueMetrics()
    metrics.remains = issue.time_remains
    metrics.efficiency = issue.efficiency
    metrics.payroll = payroll['total_payroll']
    metrics.paid = payroll['total_paid']

    return metrics


class IssuesContainerMetrics:
    """Issues container metrics."""

    time_estimate: int = 0
    time_spent: int = 0
    time_remains: int = 0
    issues_count: int = 0
    issues_closed_count: int = 0
    issues_opened_count: int = 0
    efficiency: float = 0.0


class IssuesContainerMetricsProvider:
    """Issues container metrics provider."""

    def fill_issues_metrics(self, metrics: IssuesContainerMetrics) -> None:
        """Fill gitlab metrics."""
        issues = Issue.objects.all()
        issues = self.filter_issues(issues)

        if not issues:
            return

        stats = issues.aggregate(
            time_estimate=Coalesce(Sum('time_estimate'), 0),
            time_spent=Coalesce(Sum('total_time_spent'), 0),
            issues_closed_count=Coalesce(
                Count('id', filter=Q(state=ISSUE_STATES.CLOSED)), 0,
            ),
            issues_opened_count=Coalesce(
                Count('id', filter=Q(state=ISSUE_STATES.OPENED)), 0,
            ),
            issues_count=Count('*'),
        )

        metrics.time_estimate = stats['time_estimate']
        metrics.time_remains = stats['time_estimate'] - stats['time_spent']

        if stats['time_spent']:
            metrics.efficiency = stats['time_estimate'] / stats['time_spent']

        metrics.time_spent = stats['time_spent']

        metrics.issues_closed_count = stats['issues_closed_count']
        metrics.issues_opened_count = stats['issues_opened_count']
        metrics.issues_count = stats['issues_count']

    def filter_issues(self, queryset: QuerySet) -> QuerySet:
        """Filter gitlab should be implemented in subclass."""
        raise NotImplementedError
