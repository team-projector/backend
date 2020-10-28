from django.db import models

from apps.development.models import Project
from apps.development.models.project import ProjectState


class ProjectsSummary:
    """Project summary."""

    count: int = 0
    archived_count: int = 0
    supporting_count: int = 0
    developing_count: int = 0


class ProjectsSummaryProvider:
    """Project summary provider."""

    def get_summary(self) -> ProjectsSummary:
        """Calculate and return summary."""
        summary = ProjectsSummary()

        self._fill_summary(summary)

        return summary

    def _fill_summary(self, summary: ProjectsSummary) -> None:
        """
        Fill summary.

        :param summary:
        :type summary: ProjectSummary
        :rtype: None
        """
        projects_summary = Project.objects.aggregate(
            count=(models.Count("*")),
            archived_count=(
                models.Count(
                    "pk",
                    filter=models.Q(state=ProjectState.ARCHIVED),
                )
            ),
            developing_count=(
                models.Count(
                    "pk",
                    filter=models.Q(state=ProjectState.DEVELOPING),
                )
            ),
            supporting_count=(
                models.Count(
                    "pk",
                    filter=models.Q(state=ProjectState.SUPPORTING),
                )
            ),
        )

        summary.archived_count = projects_summary["archived_count"]
        summary.developing_count = projects_summary["developing_count"]
        summary.supporting_count = projects_summary["supporting_count"]
        summary.count = projects_summary["count"]


def get_projects_summary() -> ProjectsSummary:
    """
    Get summary for projects.

    :rtype: ProjectsSummary
    """
    return ProjectsSummaryProvider().get_summary()
