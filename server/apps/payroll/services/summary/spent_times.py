# -*- coding: utf-8 -*-

from django.db.models import QuerySet


class IssuesSpentTimesSummary:
    """Issues spent times summary."""

    spent: int = 0
    closed_spent: int = 0
    opened_spent: int = 0

    def __init__(
        self,
        spent=0,
        closed_spent=0,
        opened_spent=0,
    ) -> None:
        self.spent = spent  # noqa WPS601
        self.closed_spent = closed_spent  # noqa WPS601
        self.opened_spent = opened_spent  # noqa WPS601


class MergeRequestsSpentTimesSummary:
    """Merge requests spent times summary."""

    spent: int = 0
    closed_spent: int = 0
    opened_spent: int = 0
    merged_spent: int = 0

    def __init__(
        self,
        spent=0,
        closed_spent=0,
        opened_spent=0,
        merged_spent=0,
    ) -> None:
        self.spent = spent  # noqa WPS601
        self.closed_spent = closed_spent  # noqa WPS601
        self.opened_spent = opened_spent  # noqa WPS601
        self.merged_spent = merged_spent  # noqa WPS601


class SpentTimesSummary:
    """Spent times summary."""

    issues: IssuesSpentTimesSummary
    merge_requests: MergeRequestsSpentTimesSummary

    def __init__(
        self,
        issues: IssuesSpentTimesSummary,
        merge_requests: MergeRequestsSpentTimesSummary,
    ):
        self.issues = issues
        self.merge_requests = merge_requests

    @property
    def spent(self) -> int:
        """Return total spent issues and merge requests."""
        return self.issues.spent + self.merge_requests.spent

    @property
    def opened_spent(self) -> int:
        """Return total spent opened issues and opened merge requests."""
        return self.issues.opened_spent + self.merge_requests.opened_spent


class SpentTimesSummaryProvider:
    """Spent times summary provider."""

    def __init__(
        self,
        queryset: QuerySet,
    ):
        self.queryset = queryset

    def execute(self) -> SpentTimesSummary:
        """Calculate summaries."""
        spent_summaries = self.queryset.summaries()

        issues_summaries = IssuesSpentTimesSummary(
            spent=spent_summaries['total_issues'],
            opened_spent=spent_summaries['opened_issues'],
            closed_spent=spent_summaries['closed_issues'],
        )

        merges_summaries = MergeRequestsSpentTimesSummary(
            spent=spent_summaries['total_merges'],
            opened_spent=spent_summaries['opened_merges'],
            closed_spent=spent_summaries['closed_merges'],
            merged_spent=spent_summaries['merged_merges'],
        )

        return SpentTimesSummary(
            issues_summaries,
            merges_summaries,
        )


def get_spent_times_summary(queryset: QuerySet) -> SpentTimesSummary:
    """Get summary about spent times."""
    return SpentTimesSummaryProvider(
        queryset,
    ).execute()
