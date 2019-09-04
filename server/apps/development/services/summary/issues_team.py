from typing import List, Optional

from django.db.models import (
    QuerySet, Sum, Count, Case, When, Q, IntegerField, Value, F
)
from django.db.models.functions import Coalesce

from apps.development.models import Team
from apps.development.models.issue import STATE_CLOSED


class TeamIssuesSummary:
    opened_count: int = 0
    percentage: float = 0.0
    remains: int = 0


class IssuesTeamSummary:
    team: Team
    issues: TeamIssuesSummary
    order_by: str


class IssuesTeamSummaryProvider:
    def __init__(self,
                 queryset: QuerySet,
                 order_by: Optional[str]):
        self.queryset = queryset
        self.order_by = order_by

    def execute(self) -> List[IssuesTeamSummary]:
        summaries_qs = self.queryset.annotate(
            time_remains=Case(
                When(
                    Q(time_estimate__gt=F('total_time_spent')) &  # noqa:W504
                    ~Q(state=STATE_CLOSED),
                    then=F('time_estimate') - F('total_time_spent')
                ),
                default=Value(0),
                output_field=IntegerField()
            ),
        ).values(
            'user__teams'
        ).annotate(
            issues_opened_count=Count('*'),
            total_time_remains=Coalesce(Sum('time_remains'), 0)
        ).order_by()

        summaries = {
            summary['user__teams']: summary
            for summary in
            summaries_qs
        }

        total_issues_count = sum(
            [
                item['issues_opened_count']
                for item in summaries_qs
            ]
        )

        team_ids = [
            item['user__teams']
            for item in summaries_qs
        ]

        team_qs = Team.objects.filter(id__in=team_ids)

        ret = []

        for t in team_qs:
            summary = IssuesTeamSummary()
            summary.team = t

            issues_summary = TeamIssuesSummary()
            issues_summary.opened_count = summaries[t.id]['issues_opened_count']
            issues_summary.remains = summaries[t.id]['total_time_remains']
            issues_summary.percentage = (
                issues_summary.opened_count / total_issues_count
            )

            summary.issues = issues_summary

            ret.append(summary)

        return ret


def get_team_summaries(queryset: QuerySet,
                       order_by: str = None) -> List[IssuesTeamSummary]:
    provider = IssuesTeamSummaryProvider(
        queryset,
        order_by
    )

    return provider.execute()
