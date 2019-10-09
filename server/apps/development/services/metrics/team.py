# -*- coding: utf-8 -*-

from django.db.models import Sum

from apps.development.models import Issue, MergeRequest, Team, TeamMember
from apps.development.models.issue import ISSUE_STATES
from apps.development.services.problems.issue import (
    annotate_issues_problems,
    filter_issues_problems,
)


class WorkItemTeamMetrics:
    """Work item team metrics."""

    count: int = 0
    opened_count: int = 0
    opened_estimated: int = 0


class IssueTeamMetrics(WorkItemTeamMetrics):
    """Issue team metrics."""


class MergeRequestTeamMetrics(WorkItemTeamMetrics):
    """Merge request team metrics."""


class TeamMetrics:
    """Team metrics."""

    problems_count: int = 0
    issues: IssueTeamMetrics
    merge_requests: MergeRequestTeamMetrics


class TeamMetricsProvider:
    """Team metrics provider."""

    def __init__(
        self,
        issues: Issue,
        merge_requests: MergeRequest,
    ):
        """Initialize self."""
        self.issues = issues
        self.merge_requests = merge_requests

    def execute(self) -> TeamMetrics:
        """Calculate and return metrics."""
        metrics = TeamMetrics()

        metrics.issues = self._get_issues_metrics()
        metrics.merge_requests = self._get_merge_requests_metrics()

        problems_issues = annotate_issues_problems(self.issues)
        problems_issues = filter_issues_problems(problems_issues)
        metrics.problems_count = problems_issues.count()

        return metrics

    def _get_issues_metrics(self) -> IssueTeamMetrics:
        issues = IssueTeamMetrics()

        issues.count = self.issues.count()
        issues.opened_count = self._get_opened_count(
            self.issues,
        )
        issues.opened_estimated = self._get_opened_estimated(
            self.issues,
        )

        return issues

    def _get_merge_requests_metrics(self) -> MergeRequestTeamMetrics:
        merge_requests = MergeRequestTeamMetrics()

        merge_requests.count = self.merge_requests.count()
        merge_requests.opened_count = self._get_opened_count(
            self.merge_requests,
        )
        merge_requests.opened_estimated = self._get_opened_estimated(
            self.merge_requests,
        )

        return merge_requests

    def _get_opened_count(self, workitems) -> int:
        return workitems.filter(state=ISSUE_STATES.opened).count()

    def _get_opened_estimated(self, workitems) -> int:
        return workitems.filter(
            state=ISSUE_STATES.opened,
        ).aggregate(
            total_time_estimate=Sum('time_estimate'),
        )['total_time_estimate']


def get_team_metrics(team: Team) -> TeamMetrics:
    """Get metrics for team."""
    users = TeamMember.objects.get_no_watchers(team)

    issues = Issue.objects.filter(user__in=users)
    merge_requests = MergeRequest.objects.filter(user__in=users)

    provider = TeamMetricsProvider(
        issues,
        merge_requests,
    )

    return provider.execute()
