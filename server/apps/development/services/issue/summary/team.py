# -*- coding: utf-8 -*-

from typing import List, Optional

from django.db import models
from django.db.models import (
    Case,
    Count,
    IntegerField,
    QuerySet,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce

from apps.development.models import Team
from apps.development.models.issue import ISSUE_STATES


class TeamIssuesSummary:
    """Team issues summary."""

    opened_count: int = 0
    percentage: float = 0.0
    remains: int = 0


class IssuesTeamSummary:
    """Issues team summary."""

    team: Team
    issues: TeamIssuesSummary
    order_by: str


class IssuesTeamSummaryProvider:
    """Issues team summary provider."""

    def __init__(
        self,
        queryset: QuerySet,
        order_by: Optional[str],
    ):
        """Initialize self."""
        self.queryset = queryset
        self.order_by = order_by

    def execute(self) -> List[IssuesTeamSummary]:
        """Calculate and return summary."""
        summaries_qs = self._get_summaries_qs()

        total_issues_count = self._get_total_issues_count(summaries_qs)

        summaries: List[IssuesTeamSummary] = []

        summaries = self._apply_summary(
            summaries,
            summaries_qs,
            total_issues_count,
        )

        return summaries

    def _apply_summary(
        self,
        summaries: List[IssuesTeamSummary],
        summaries_qs: QuerySet,
        total_issues_count: int,
    ):
        summaries_team = {
            summary['user__teams']: summary
            for summary in
            summaries_qs
        }

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
        issues_summary = TeamIssuesSummary()
        issues_summary.opened_count = summaries[team.id][
            'issues_opened_count'
        ]
        issues_summary.remains = summaries[team.id][
            'total_time_remains'
        ]
        issues_summary.percentage = (
            issues_summary.opened_count / total_issues_count
        )
        return issues_summary

    def _get_summaries_qs(self) -> QuerySet:
        return self.queryset.annotate(
            time_remains=Case(
                When(
                    models.Q(time_estimate__gt=models.F('total_time_spent'))
                    & ~models.Q(state=ISSUE_STATES.CLOSED),
                    then=(
                        models.F('time_estimate') - models.F('total_time_spent')
                    ),
                ),
                default=Value(0),
                output_field=IntegerField(),
            ),
        ).values(
            'user__teams',
        ).annotate(
            issues_opened_count=Count('*'),
            total_time_remains=Coalesce(Sum('time_remains'), 0),
        ).order_by()

    def _get_total_issues_count(
        self,
        summaries_qs: QuerySet,
    ) -> int:
        return sum(
            summary['issues_opened_count']
            for summary in summaries_qs
        )

    def _get_team_qs(
        self,
        summaries_qs: QuerySet,
    ) -> QuerySet:
        team_ids = [
            summary['user__teams']
            for summary in summaries_qs
        ]

        return Team.objects.filter(id__in=team_ids)


def get_team_summaries(
    queryset: QuerySet,
    order_by: Optional[str] = None,
) -> List[IssuesTeamSummary]:
    """Get summaries for team."""
    provider = IssuesTeamSummaryProvider(
        queryset,
        order_by,
    )

    return provider.execute()
