from django.db import models
from django.db.models.functions import Coalesce

from apps.development.models import ProjectGroup
from apps.development.services.issue.metrics import (
    IssuesContainerMetrics,
    IssuesContainerMetricsProvider,
)
from apps.payroll.models import SpentTime


class ProjectGroupMetrics(IssuesContainerMetrics):
    """Project group metrics."""

    budget: float = 0
    budget_spent: float = 0
    budget_remains: float = 0
    payroll: float = 0.0
    profit: float = 0


class ProjectGroupMetricsProvider(IssuesContainerMetricsProvider):
    """Project group metrics provider."""

    def __init__(self, project_group: ProjectGroup):
        """Initialize self."""
        self.project_group = project_group

    def filter_issues(self, queryset: models.QuerySet) -> models.QuerySet:
        """Filter issues."""
        return queryset.filter(
            milestone__isnull=False,
            project__group=self.project_group,
        )

    def get_metrics(self) -> ProjectGroupMetrics:
        """Calculate and return metrics."""
        metrics = ProjectGroupMetrics()

        self.fill_issues_metrics(metrics)
        self._fill_payroll_metrics(metrics)
        self._fill_budget_metrics(metrics)

        if metrics.budget:
            metrics.profit = metrics.budget - metrics.payroll
            metrics.budget_remains = metrics.budget - metrics.budget_spent

        return metrics

    def _fill_payroll_metrics(self, metrics: ProjectGroupMetrics) -> None:
        """
        Fill payroll metrics.

        :param metrics:
        :type metrics: ProjectGroupMetrics
        :rtype: None
        """
        payroll = SpentTime.objects.filter(
            models.Q(
                issues__milestone__isnull=False,
                issues__project__group=self.project_group,
            )
            | models.Q(
                mergerequests__milestone__isnull=False,
                mergerequests__project__group=self.project_group,
            ),
        ).aggregate(
            total_sum=Coalesce(models.Sum("sum"), 0),
            total_customer_sum=Coalesce(models.Sum("customer_sum"), 0),
        )

        metrics.payroll = payroll["total_sum"]
        metrics.budget_spent = payroll["total_customer_sum"]

    def _fill_budget_metrics(self, metrics: ProjectGroupMetrics) -> None:
        """
        Fill project group budget from milestones.

        :param metrics:
        :type metrics: ProjectGroupMetrics
        :rtype: None
        """
        milestones_budget = self.project_group.milestones.aggregate(
            total_budget=Coalesce(models.Sum("budget"), 0),
        )

        metrics.budget = milestones_budget["total_budget"]


def get_project_group_metrics(
    project_group: ProjectGroup,
) -> ProjectGroupMetrics:
    """
    Get metrics for project group.

    :param project_group:
    :type project_group: ProjectGroup
    :rtype: ProjectGroupMetrics
    """
    return ProjectGroupMetricsProvider(project_group).get_metrics()
