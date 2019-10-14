# -*- coding: utf-8 -*-

from typing import List

from django.db.models import Count, QuerySet, Sum

from apps.development.models.issue import ISSUE_STATES
from apps.development.services import issue as issue_service
from apps.payroll.models import SpentTime


class IssuesSummary:
    """Issues summary."""

    count: int = 0
    opened_count: int = 0
    closed_count: int = 0
    time_spent: int = 0
    problems_count: int = 0
    projects: List[issue_service.IssuesProjectSummary] = []
    teams: List[issue_service.IssuesTeamSummary] = []

    queryset: QuerySet


class IssuesSummaryProvider:
    """Issues summary provider."""

    def __init__(
        self,
        queryset: QuerySet,
        **kwargs,
    ):
        """Initialize self."""
        self._queryset = queryset
        self._options = kwargs

    def execute(self) -> IssuesSummary:
        """Calculate and return summary."""
        summary = IssuesSummary()
        summary.queryset = self._queryset

        for count_state in self._get_counts_by_state():
            summary.count += count_state['count']

            if count_state['state'] == ISSUE_STATES.opened:
                summary.opened_count = count_state['count']
            elif count_state['state'] == ISSUE_STATES.closed:
                summary.closed_count = count_state['count']

        summary.time_spent = self._get_time_spent()
        summary.problems_count = self._get_problems_count()

        return summary

    def _get_counts_by_state(self) -> QuerySet:
        return self._queryset.values(
            'state',
        ).annotate(
            count=Count('*'),
        ).order_by()

    def _get_time_spent(self) -> int:  # noqa: C901
        queryset = SpentTime.objects.filter(issues__isnull=False)

        if self._options.get('due_date'):
            queryset = queryset.filter(date=self._options['due_date'])

        if self._options.get('user'):
            queryset = queryset.filter(user=self._options['user'])

        if self._options.get('team'):
            queryset = queryset.filter(user__teams=self._options['team'])

        if self._options.get('project'):
            queryset = queryset.filter(issues__project=self._options['project'])

        if self._options.get('state'):
            queryset = queryset.filter(issues__state=self._options['state'])

        if self._options.get('milestone'):
            queryset = queryset.filter(
                issues__milestone=self._options['milestone'],
            )

        if self._options.get('ticket'):
            queryset = queryset.filter(issues__ticket=self._options['ticket'])

        return queryset.aggregate(
            total_time_spent=Sum('time_spent'),
        )['total_time_spent'] or 0

    def _get_problems_count(self) -> int:
        queryset = issue_service.annotate_problems(self._queryset)
        queryset = issue_service.filter_problems(queryset)

        return queryset.count()


def get_issues_summary(
    queryset: QuerySet,
    **kwargs,
) -> IssuesSummary:
    """Get summary for issues."""
    return IssuesSummaryProvider(
        queryset,
        **kwargs,
    ).execute()
