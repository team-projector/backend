from datetime import datetime
from typing import List, NamedTuple, Optional

from django.db import models
from django.db.models.functions import Coalesce

from apps.development.models import Project
from apps.development.models.issue import IssueState


class ProjectIssuesSummary(NamedTuple):
    """Project issues summary."""

    opened_count: int = 0
    percentage: float = 0
    remains: int = 0


class IssuesProjectSummary(NamedTuple):
    """Issues project summary."""

    project: Project
    issues: ProjectIssuesSummary


class _SortProjectSummaries:
    def sort(
        self,
        summaries: List[IssuesProjectSummary],
        sort: Optional[str],
    ):
        if sort == "issues__remains":
            return sorted(summaries, key=self._get_remains)
        elif sort == "-issues__remains":
            return sorted(summaries, key=self._get_remains, reverse=True)
        return sorted(summaries, key=self._get_min_due_date)

    def _get_min_due_date(self, summary: IssuesProjectSummary):
        """Get minimum due date."""
        sorted_milestones = sorted(
            summary.project.active_milestones,
            key=self._get_key,
        )
        if sorted_milestones:
            return sorted_milestones[0].due_date or datetime.max.date()

        return datetime.max.date()

    def _get_remains(self, summary: IssuesProjectSummary):
        """Get remains from summary."""
        return summary.issues.remains

    def _get_key(self, milestone):
        """
        Get key.

        :param milestone:
        """
        return getattr(milestone, "due_date", None) or datetime.max.date()


sort_project_summaries = _SortProjectSummaries().sort


class IssuesProjectSummaryProvider:
    """Issues project summary provider."""

    def __init__(
        self,
        queryset: models.QuerySet,
        sort: Optional[str],
        is_active: Optional[bool],
        state: Optional[str],
    ):
        """Initialize self."""
        self.queryset = queryset
        self.sort = sort
        self.is_active = is_active
        self.state = state

    def execute(self) -> List[IssuesProjectSummary]:
        """Calculate and return summary."""
        summaries_qs = self._get_summaries_qs()

        total_issues_count = self._get_total_issues_count(summaries_qs)

        summaries = self._get_summaries(summaries_qs, total_issues_count)
        return sort_project_summaries(summaries, self.sort)

    def _get_summaries(
        self,
        summaries_qs: models.QuerySet,
        total_issues_count: int,
    ) -> List[IssuesProjectSummary]:
        """
        Get summaries.

        :param summaries_qs:
        :type summaries_qs: models.QuerySet
        :param total_issues_count:
        :type total_issues_count: int
        :rtype: List[IssuesProjectSummary]
        """
        summaries_project = {
            summary["project"]: summary for summary in summaries_qs
        }

        summaries: List[IssuesProjectSummary] = []

        for project in self._get_project_qs(summaries_qs):
            summary = IssuesProjectSummary(
                project=project,
                issues=self._get_issues_summary(
                    summaries_project,
                    project,
                    total_issues_count,
                ),
            )
            summaries.append(summary)

        return summaries

    def _get_issues_summary(
        self,
        summaries,
        project: Project,
        total_issues_count: int,
    ) -> ProjectIssuesSummary:
        """
        Get issues summary.

        :param summaries:
        :param project:
        :type project: Project
        :param total_issues_count:
        :type total_issues_count: int
        :rtype: ProjectIssuesSummary
        """
        opened_count = summaries[project.id]["issues_opened_count"]

        return ProjectIssuesSummary(
            opened_count=opened_count,
            remains=summaries[project.id]["total_time_remains"],
            percentage=(opened_count / total_issues_count),
        )

    def _get_summaries_qs(self) -> models.QuerySet:
        """
        Get summaries qs.

        :rtype: models.QuerySet
        """
        return (
            self.queryset.annotate(
                time_remains=models.Case(
                    models.When(
                        models.Q(  # noqa: WPS465
                            time_estimate__gt=models.F("total_time_spent"),
                        )
                        & ~models.Q(state=IssueState.CLOSED),
                        then=(
                            models.F("time_estimate")
                            - models.F("total_time_spent")
                        ),
                    ),
                    default=models.Value(0),
                    output_field=models.IntegerField(),
                ),
            )
            .values("project")
            .annotate(
                issues_opened_count=models.Count("*"),
                total_time_remains=Coalesce(models.Sum("time_remains"), 0),
            )
            .order_by()
        )

    def _get_total_issues_count(self, summaries_qs: models.QuerySet) -> int:
        """
        Get total issues count.

        :param summaries_qs:
        :type summaries_qs: models.QuerySet
        :rtype: int
        """
        return sum(summary["issues_opened_count"] for summary in summaries_qs)

    def _get_project_qs(self, summaries_qs: models.QuerySet) -> List[Project]:
        """
        Get project qs.

        :param summaries_qs:
        :type summaries_qs: models.QuerySet
        :rtype: List[Project]
        """
        project_ids = [summary["project"] for summary in summaries_qs]
        queryset = Project.objects.filter(id__in=project_ids)

        if self.is_active is not None:
            queryset = queryset.filter(is_active=self.is_active)

        if self.state is not None:
            queryset = queryset.filter(state=self.state)

        return queryset


def get_project_summaries(
    queryset: models.QuerySet,
    sort: Optional[str] = None,
    is_active: Optional[bool] = None,
    state: Optional[str] = None,
) -> List[IssuesProjectSummary]:
    """Get summaries for project."""
    provider = IssuesProjectSummaryProvider(
        queryset,
        sort,
        is_active,
        state,
    )

    return provider.execute()
