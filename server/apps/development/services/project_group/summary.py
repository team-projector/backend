from django.db import models

from apps.development.models import ProjectGroup
from apps.development.models.project import ProjectState


class ProjectGroupsSummary:
    """Project groups summary."""

    count: int = 0
    archived_count: int = 0
    supporting_count: int = 0
    developing_count: int = 0


class ProjectGroupsSummaryProvider:
    """Project groups summary provider."""

    def get_summary(self) -> ProjectGroupsSummary:
        """Calculate and return summary."""
        summary = ProjectGroupsSummary()

        self._fill_summary(summary)

        return summary

    def _fill_summary(self, summary: ProjectGroupsSummary) -> None:
        """
        Fill summary.

        :param summary:
        :type summary: ProjectGroupsSummary
        :rtype: None
        """
        projects_summary = ProjectGroup.objects.aggregate(
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


def get_project_groups_summary() -> ProjectGroupsSummary:
    """
    Get summary for project groups.

    :rtype: ProjectGroupsSummary
    """
    return ProjectGroupsSummaryProvider().get_summary()
