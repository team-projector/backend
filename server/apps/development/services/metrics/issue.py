# -*- coding: utf-8 -*-

from apps.development.models import Issue
from apps.payroll.models import SpentTime


class IssueMetrics:
    """Issue metrics."""

    remains: int = 0
    efficiency: float = 0
    payroll: float = 0
    paid: float = 0


def get_issue_metrics(issue: Issue) -> IssueMetrics:
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
