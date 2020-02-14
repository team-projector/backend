# -*- coding: utf-8 -*-

from datetime import datetime
from typing import List, Optional

from django.db import models
from django.db.models.functions import Coalesce

from apps.development.models import Project
from apps.development.models.issue import IssueState


def get_min_due_date(project):
    """Get minimum due date."""
    sorted_milestones = sorted(project.active_milestones, key=_get_key)
    if sorted_milestones:
        return sorted_milestones[0].due_date or datetime.max.date()

    return datetime.max.date()


def _get_key(milestone):
    return getattr(milestone, "due_date", None) or datetime.max.date()


class ProjectIssuesSummary:
    """Project issues summary."""

    opened_count: int = 0
    percentage: float = 0.0
    remains: int = 0


class IssuesProjectSummary:
    """Issues project summary."""

    project: Project
    issues: ProjectIssuesSummary
    order_by: str


class IssuesProjectSummaryProvider:
    """Issues project summary provider."""

    def __init__(
        self,
        queryset: models.QuerySet,
        order_by: Optional[str],
    ):
        """Initialize self."""
        self.queryset = queryset
        self.order_by = order_by

    def execute(self) -> List[IssuesProjectSummary]:
        """Calculate and return summary."""
        summaries_qs = self._get_summaries_qs()

        total_issues_count = self._get_total_issues_count(summaries_qs)

        summaries: List[IssuesProjectSummary] = []

        summaries = self._apply_summary(
            summaries,
            summaries_qs,
            total_issues_count,
        )

        return summaries

    def _apply_summary(
        self,
        summaries: List[IssuesProjectSummary],
        summaries_qs: models.QuerySet,
        total_issues_count: int,
    ) -> List[IssuesProjectSummary]:
        summaries_project = {
            summary["project"]: summary
            for summary in
            summaries_qs
        }

        for project in self._get_project_qs(summaries_qs):
            summary = IssuesProjectSummary()
            summaries.append(summary)

            summary.project = project
            summary.issues = self._get_issues_summary(
                summaries_project,
                project,
                total_issues_count,
            )

        return summaries

    def _get_issues_summary(
        self,
        summaries,
        project: Project,
        total_issues_count: int,
    ) -> ProjectIssuesSummary:
        issues_summary = ProjectIssuesSummary()
        issues_summary.opened_count = summaries[project.id][
            "issues_opened_count"
        ]
        issues_summary.remains = summaries[project.id][
            "total_time_remains"
        ]
        issues_summary.percentage = (
            issues_summary.opened_count / total_issues_count
        )

        return issues_summary

    def _get_summaries_qs(self) -> models.QuerySet:
        return self.queryset.annotate(
            time_remains=models.Case(
                models.When(
                    models.Q(time_estimate__gt=models.F("total_time_spent"))
                    & ~models.Q(state=IssueState.CLOSED),
                    then=(
                        models.F("time_estimate") - models.F("total_time_spent")
                    ),
                ),
                default=models.Value(0),
                output_field=models.IntegerField(),
            ),
        ).values(
            "project",
        ).annotate(
            issues_opened_count=models.Count("*"),
            total_time_remains=Coalesce(models.Sum("time_remains"), 0),
        ).order_by()

    def _get_total_issues_count(
        self,
        summaries_qs: models.QuerySet,
    ) -> int:
        return sum(
            summary["issues_opened_count"]
            for summary in summaries_qs
        )

    def _get_project_qs(
        self,
        summaries_qs: models.QuerySet,
    ) -> List[Project]:
        project_ids = [
            summary["project"]
            for summary in summaries_qs
        ]

        projects_qs = Project.objects.filter(id__in=project_ids)
        projects_qs = sorted(projects_qs, key=get_min_due_date)

        return projects_qs


def get_project_summaries(
    queryset: models.QuerySet,
    order_by: Optional[str] = None,
) -> List[IssuesProjectSummary]:
    """Get summaries for project."""
    provider = IssuesProjectSummaryProvider(
        queryset,
        order_by,
    )

    return provider.execute()
