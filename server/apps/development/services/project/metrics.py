from django.db import models
from django.db.models.functions import Coalesce

from apps.development.models import Project
from apps.development.services.issue.metrics import (
    IssuesContainerMetrics,
    IssuesContainerMetricsProvider,
)
from apps.payroll.models import SpentTime


class ProjectMetrics(IssuesContainerMetrics):
    """Project metrics."""

    budget: float = 0
    budget_spent: float = 0
    budget_remains: float = 0
    payroll: float = 0.0
    profit: float = 0


class ProjectMetricsProvider(IssuesContainerMetricsProvider):
    """Project metrics provider."""

    def __init__(self, project: Project):
        """Initialize self."""
        self.project = project

    def filter_issues(self, queryset: models.QuerySet) -> models.QuerySet:
        """Filter issues."""
        return queryset.filter(milestone__isnull=False, project=self.project)

    def get_metrics(self) -> ProjectMetrics:
        """Calculate and return metrics."""
        metrics = ProjectMetrics()

        self.fill_issues_metrics(metrics)
        self._fill_payroll_metrics(metrics)
        self._fill_budget_metrics(metrics)

        metrics.profit = metrics.budget - metrics.payroll
        metrics.budget_remains = metrics.budget - metrics.budget_spent

        return metrics

    def _fill_payroll_metrics(self, metrics: ProjectMetrics) -> None:
        """
        Fill payroll metrics.

        :param metrics:
        :type metrics: ProjectMetrics
        :rtype: None
        """
        payroll = SpentTime.objects.filter(
            models.Q(
                issues__milestone__isnull=False,
                issues__project=self.project,
            )
            | models.Q(
                mergerequests__milestone__isnull=False,
                mergerequests__project=self.project,
            ),
        ).aggregate(
            total_sum=Coalesce(models.Sum("sum"), 0),
            total_customer_sum=Coalesce(models.Sum("customer_sum"), 0),
        )

        metrics.payroll = payroll["total_sum"]
        metrics.budget_spent = payroll["total_customer_sum"]

    def _fill_budget_metrics(self, metrics: ProjectMetrics) -> None:
        """
        Fill project budget from milestones.

        :param metrics:
        :type metrics: ProjectMetrics
        :rtype: None
        """
        milestones_budget = self.project.milestones.aggregate(
            total_budget=Coalesce(models.Sum("budget"), 0),
        )

        metrics.budget = milestones_budget["total_budget"]


def get_project_metrics(project: Project) -> ProjectMetrics:
    """
    Get metrics for project.

    :param project:
    :type project: Project
    :rtype: ProjectMetrics
    """
    return ProjectMetricsProvider(project).get_metrics()
