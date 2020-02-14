# -*- coding: utf-8 -*-

from django.db import models

from apps.development.models.merge_request import MergeRequestState


class MergeRequestsSummary:
    """Merge requests summary."""

    count: int = 0
    opened_count: int = 0
    closed_count: int = 0
    merged_count: int = 0


class MergeRequestsSummaryProvider:
    """Merge requests summary provider."""

    def __init__(self, queryset: models.QuerySet):
        """Initialize self."""
        self.queryset = queryset

    def execute(self) -> MergeRequestsSummary:
        """Calculate and return summary."""
        summary = MergeRequestsSummary()

        merge_requests_counts = self.get_counts()

        summary.count = merge_requests_counts["count"]
        summary.opened_count = merge_requests_counts["opened_count"]
        summary.closed_count = merge_requests_counts["closed_count"]
        summary.merged_count = merge_requests_counts["merged_count"]

        return summary

    def get_counts(self) -> models.QuerySet:
        """Get counts by state."""
        return self.queryset.aggregate(
            count=self._count(),
            opened_count=self._count(state=MergeRequestState.OPENED),
            closed_count=self._count(state=MergeRequestState.CLOSED),
            merged_count=self._count(state=MergeRequestState.MERGED),
        )

    def _count(self, **filters) -> models.Count:
        return models.Count("id", filter=models.Q(**filters))


def get_merge_requests_summary(
    queryset: models.QuerySet,
) -> MergeRequestsSummary:
    """Get summary for merge requests."""
    return MergeRequestsSummaryProvider(queryset).execute()
