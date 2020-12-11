from django.db import models
from django.db.models import QuerySet
from django.db.models.functions import Coalesce


class _AggregationService:
    def aggregate_payrolls(self, spent_times: QuerySet):
        """Get total sum payroll and paid."""
        return self.annotate_payrolls(spent_times).aggregate(
            total_payroll=Coalesce(models.Sum("sum"), 0),
            total_paid=Coalesce(models.Sum("paid"), 0),
        )

    def summaries(self, spent_times: QuerySet):
        """Get spent time summaries."""
        from apps.development.models import issue  # noqa: WPS433
        from apps.development.models.merge_request import (  # noqa: WPS433
            MergeRequestState,
        )

        return spent_times.aggregate(
            total_issues=self._sum(issues__isnull=False),
            opened_issues=self._sum(issues__state=issue.IssueState.OPENED),
            closed_issues=self._sum(issues__state=issue.IssueState.CLOSED),
            total_merges=self._sum(mergerequests__isnull=False),
            opened_merges=self._sum(
                mergerequests__state=MergeRequestState.OPENED,
            ),
            closed_merges=self._sum(
                mergerequests__state=MergeRequestState.CLOSED,
            ),
            merged_merges=self._sum(
                mergerequests__state=MergeRequestState.MERGED,
            ),
        )

    def annotate_payrolls(
        self,
        spent_times: QuerySet,
    ) -> models.QuerySet:
        """Get total sum paid."""
        return spent_times.annotate(
            paid=models.Case(
                models.When(salary__isnull=False, then=models.F("sum")),
                default=0,
                output_field=models.FloatField(),
            ),
        )

    def _sum(self, **filters) -> Coalesce:
        """
        Sum.

        :rtype: Coalesce
        """
        return Coalesce(
            models.Sum("time_spent", filter=models.Q(**filters)),
            0,
        )


spent_time_aggregation_service = _AggregationService()


class IssuesSpentTimesSummary:
    """Issues spent times summary."""

    spent: int = 0
    closed_spent: int = 0
    opened_spent: int = 0

    def __init__(self, spent=0, closed_spent=0, opened_spent=0) -> None:
        """Initialize issues spent times summary."""
        self.spent = spent  # noqa: WPS601
        self.closed_spent = closed_spent  # noqa: WPS601
        self.opened_spent = opened_spent  # noqa: WPS601


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
        """Initialize merge requests spent times summary."""
        self.spent = spent  # noqa: WPS601
        self.closed_spent = closed_spent  # noqa: WPS601
        self.opened_spent = opened_spent  # noqa: WPS601
        self.merged_spent = merged_spent  # noqa: WPS601


class SpentTimesSummary:
    """Spent times summary."""

    issues: IssuesSpentTimesSummary
    merge_requests: MergeRequestsSpentTimesSummary

    def __init__(
        self,
        issues: IssuesSpentTimesSummary,
        merge_requests: MergeRequestsSpentTimesSummary,
    ):
        """Initialize spent times summary."""
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

    @property
    def closed_spent(self) -> int:
        """Return total spent closed issues and closed merge requests."""
        return (
            self.issues.closed_spent
            + self.merge_requests.closed_spent
            + self.merge_requests.merged_spent
        )


class SpentTimesSummaryProvider:
    """Spent times summary provider."""

    def __init__(
        self,
        queryset: QuerySet,
    ):
        """Initialize spent times summary provider."""
        self.queryset = queryset

    def execute(self) -> SpentTimesSummary:
        """Calculate summaries."""
        spent_summaries = spent_time_aggregation_service.summaries(
            self.queryset,
        )

        issues_summaries = IssuesSpentTimesSummary(
            spent=spent_summaries["total_issues"],
            opened_spent=spent_summaries["opened_issues"],
            closed_spent=spent_summaries["closed_issues"],
        )

        merges_summaries = MergeRequestsSpentTimesSummary(
            spent=spent_summaries["total_merges"],
            opened_spent=spent_summaries["opened_merges"],
            closed_spent=spent_summaries["closed_merges"],
            merged_spent=spent_summaries["merged_merges"],
        )

        return SpentTimesSummary(issues_summaries, merges_summaries)


def get_summary(queryset: QuerySet) -> SpentTimesSummary:
    """Get summary about spent times."""
    return SpentTimesSummaryProvider(queryset).execute()
