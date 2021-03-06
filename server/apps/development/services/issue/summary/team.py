from typing import List, Optional

from django.db import models
from django.db.models.functions import Coalesce

from apps.development.models import Team
from apps.development.models.issue import IssueState


class TeamIssuesSummary:
    """Team issues summary."""

    opened_count: int = 0
    percentage: float = 0
    remains: int = 0


class IssuesTeamSummary:
    """Issues team summary."""

    team: Team
    issues: TeamIssuesSummary
    sort: str


class IssuesTeamSummaryProvider:
    """Issues team summary provider."""

    def __init__(
        self,
        queryset: models.QuerySet,
        sort: Optional[str],
    ):
        """Initialize self."""
        self.queryset = queryset
        self.sort = sort

    def execute(self) -> List[IssuesTeamSummary]:
        """Calculate and return summary."""
        summaries_qs = self._get_summaries_qs()

        total_issues_count = self._get_total_issues_count(summaries_qs)

        return self._get_summaries(summaries_qs, total_issues_count)

    def _get_summaries(
        self,
        summaries_qs: models.QuerySet,
        total_issues_count: int,
    ):
        """
        Get summaries.

        :param summaries_qs:
        :type summaries_qs: models.QuerySet
        :param total_issues_count:
        :type total_issues_count: int
        """
        summaries_team = {
            summary["user__teams"]: summary for summary in summaries_qs
        }

        summaries: List[IssuesTeamSummary] = []

        team_qs = self._get_team_qs(summaries_qs)

        for team in team_qs:
            summary = IssuesTeamSummary()
            summaries.append(summary)

            summary.team = team
            summary.issues = self._get_issues_summary(
                summaries_team,
                team,
                total_issues_count,
            )

        return summaries

    def _get_issues_summary(
        self,
        summaries,
        team: Team,
        total_issues_count: int,
    ) -> TeamIssuesSummary:
        """
        Get issues summary.

        :param summaries:
        :param team:
        :type team: Team
        :param total_issues_count:
        :type total_issues_count: int
        :rtype: TeamIssuesSummary
        """
        issues_summary = TeamIssuesSummary()
        issues_summary.opened_count = summaries[team.id]["issues_opened_count"]
        issues_summary.remains = summaries[team.id]["total_time_remains"]
        issues_summary.percentage = (
            issues_summary.opened_count / total_issues_count
        )
        return issues_summary

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
            .values("user__teams")
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

    def _get_team_qs(self, summaries_qs: models.QuerySet) -> models.QuerySet:
        """
        Get team qs.

        :param summaries_qs:
        :type summaries_qs: models.QuerySet
        :rtype: models.QuerySet
        """
        team_ids = [summary["user__teams"] for summary in summaries_qs]

        return Team.objects.filter(id__in=team_ids)


def get_team_summaries(
    queryset: models.QuerySet,
    sort: Optional[str] = None,
) -> List[IssuesTeamSummary]:
    """Get summaries for team."""
    provider = IssuesTeamSummaryProvider(queryset, sort)

    return provider.execute()
