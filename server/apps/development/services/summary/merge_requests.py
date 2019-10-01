# -*- coding: utf-8 -*-

from django.db.models import Count, Q, QuerySet

from apps.development.models.merge_request import MERGE_REQUESTS_STATES


class MergeRequestsSummary:
    count: int = 0
    opened_count: int = 0
    closed_count: int = 0
    merged_count: int = 0


class MergeRequestsSummaryProvider:
    def __init__(self, queryset: QuerySet):
        self.queryset = queryset

    def execute(self) -> MergeRequestsSummary:
        summary = MergeRequestsSummary()

        merge_requests_counts = self.get_counts_by_state()

        summary.count = merge_requests_counts['count']
        summary.opened_count = merge_requests_counts['opened_count']
        summary.closed_count = merge_requests_counts['closed_count']
        summary.merged_count = merge_requests_counts['merged_count']

        return summary

    def get_counts_by_state(self):
        return self.queryset.aggregate(
            count=self._count(),
            opened_count=self._count(state=MERGE_REQUESTS_STATES.opened),
            closed_count=self._count(state=MERGE_REQUESTS_STATES.closed),
            merged_count=self._count(state=MERGE_REQUESTS_STATES.merged),
        )

    @staticmethod
    def _count(**filters):
        return Count('id', filter=Q(**filters))


def get_merge_requests_summary(queryset: QuerySet) -> MergeRequestsSummary:
    return MergeRequestsSummaryProvider(queryset).execute()
