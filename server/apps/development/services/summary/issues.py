# -*- coding: utf-8 -*-

from typing import List

from django.db.models import Count, QuerySet, Sum

from apps.development.models.issue import ISSUE_STATES
from apps.development.services.problems.issue import (
    annotate_issues_problems,
    filter_issues_problems,
)
from apps.payroll.models import SpentTime

from .issues_project import IssuesProjectSummary
from .issues_team import IssuesTeamSummary


class IssuesSummary:
    count: int = 0
    opened_count: int = 0
    closed_count: int = 0
    time_spent: int = 0
    problems_count: int = 0
    projects: List[IssuesProjectSummary] = []
    teams: List[IssuesTeamSummary] = []

    queryset: QuerySet


class IssuesSummaryProvider:
    def __init__(
        self,
        queryset: QuerySet,
        **kwargs,
    ):
        self._queryset = queryset
        self._options = kwargs

    def execute(self) -> IssuesSummary:
        summary = IssuesSummary()
        summary.queryset = self._queryset

        for item in self._get_counts_by_state():
            summary.count += item['count']

            if item['state'] == ISSUE_STATES.opened:
                summary.opened_count = item['count']
            elif item['state'] == ISSUE_STATES.closed:
                summary.closed_count = item['count']

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

        return queryset.aggregate(
            total_time_spent=Sum('time_spent'),
        )['total_time_spent'] or 0

    def _get_problems_count(self) -> int:
        queryset = annotate_issues_problems(self._queryset)
        queryset = filter_issues_problems(queryset)

        return queryset.count()


def get_issues_summary(
    queryset: QuerySet,
    **kwargs,
) -> IssuesSummary:
    return IssuesSummaryProvider(
        queryset,
        **kwargs,
    ).execute()
