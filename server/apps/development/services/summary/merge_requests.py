from typing import Optional

from django.db.models import QuerySet, Count

from apps.development.models import MergeRequest, Project, Team
from apps.users.models import User


class MergeRequestsSummary:
    count: int = 0
    opened_count: int = 0
    closed_count: int = 0
    merged_count: int = 0


class MergeRequestsSummaryProvider:
    def __init__(self,
                 queryset: QuerySet,
                 project: Optional[Project],
                 team: Optional[Team],
                 user: Optional[User]):
        self.queryset = queryset
        self.project = project
        self.team = team
        self.user = user

    def execute(self) -> MergeRequestsSummary:
        summary = MergeRequestsSummary()

        total_count = 0
        for item in self._get_counts_by_state():
            if item['state'] == MergeRequest.STATE.opened:
                summary.opened_count = item['count']
                total_count += item['count']
            elif item['state'] == MergeRequest.STATE.closed:
                summary.closed_count = item['count']
                total_count += item['count']
            elif item['state'] == MergeRequest.STATE.merged:
                summary.merged_count = item['count']
                total_count += item['count']
            elif item['state'] is None:
                total_count += item['count']

        summary.count = total_count

        return summary

    def _get_counts_by_state(self) -> QuerySet:
        return self.queryset.values(
            'state'
        ).annotate(
            count=Count('*')
        ).order_by()


def get_merge_requests_summary(queryset: QuerySet,
                               project: Optional[Project],
                               team: Optional[Team],
                               user: Optional[User]) -> MergeRequestsSummary:
    provider = MergeRequestsSummaryProvider(
        queryset,
        project,
        team,
        user
    )

    return provider.execute()
