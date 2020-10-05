# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce

from apps.development.models import Issue
from apps.development.models.issue import IssueState
from apps.payroll.models import SpentTime
from apps.payroll.services.spent_time.summary import (
    spent_time_aggregation_service,
)
from apps.users.models import User


class IssueMetrics:
    """Issue metrics."""

    remains: int = 0
    efficiency: float = 0
    payroll: float = 0
    paid: float = 0


def get_issue_metrics(issue: Issue) -> IssueMetrics:
    """Get metrics for issue."""
    payroll = spent_time_aggregation_service.aggregate_payrolls(
        SpentTime.objects.filter(issues__id=issue.id),
    )

    metrics = IssueMetrics()
    metrics.remains = issue.time_remains
    metrics.efficiency = issue.efficiency or 0
    metrics.payroll = payroll["total_payroll"]
    metrics.paid = payroll["total_paid"]

    return metrics


def get_user_time_spent(issue: Issue, user: User) -> int:
    """Get time spent for issue."""
    return (
        issue.time_spents.filter(user=user).aggregate(
            total_user_time_spent=Sum("time_spent"),
        )["total_user_time_spent"]
        or 0
    )


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
            time_estimate=Coalesce(models.Sum("time_estimate"), 0),
            time_spent=Coalesce(models.Sum("total_time_spent"), 0),
            issues_closed_count=Coalesce(
                models.Count("id", filter=models.Q(state=IssueState.CLOSED)),
                0,
            ),
            issues_opened_count=Coalesce(
                models.Count("id", filter=models.Q(state=IssueState.OPENED)),
                0,
            ),
            issues_count=models.Count("*"),
        )

        metrics.time_estimate = stats["time_estimate"]
        metrics.time_remains = stats["time_estimate"] - stats["time_spent"]

        if stats["time_spent"]:
            metrics.efficiency = stats["time_estimate"] / stats["time_spent"]

        metrics.time_spent = stats["time_spent"]

        metrics.issues_closed_count = stats["issues_closed_count"]
        metrics.issues_opened_count = stats["issues_opened_count"]
        metrics.issues_count = stats["issues_count"]

    def filter_issues(self, queryset: models.QuerySet) -> models.QuerySet:
        """Filter gitlab should be implemented in subclass."""
        raise NotImplementedError
