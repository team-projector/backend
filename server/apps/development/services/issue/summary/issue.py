# -*- coding: utf-8 -*-

from typing import List

from django.db.models import Count, QuerySet, Sum

from apps.development.models.issue import IssueState
from apps.development.services.issue.problems import (
    annotate_issue_problems,
    filter_issue_problems,
)
from apps.development.services.issue.summary import (
    IssuesProjectSummary,
    IssuesTeamSummary,
)
from apps.payroll.models import SpentTime


class IssuesSummary:
    """Issues summary."""

    count: int = 0
    opened_count: int = 0
    closed_count: int = 0
    time_spent: int = 0
    problems_count: int = 0
    projects: List[IssuesProjectSummary] = []
    teams: List[IssuesTeamSummary] = []

    queryset: QuerySet


class IssuesSummaryProvider:
    """Issues summary provider."""

    def __init__(
        self, queryset: QuerySet, **kwargs,
    ):
        """Initialize self."""
        self._queryset = queryset
        self._options = kwargs

    def execute(self) -> IssuesSummary:
        """Calculate and return summary."""
        summary = IssuesSummary()
        summary.queryset = self._queryset

        for count_state in self._get_counts_by_state():
            summary.count += count_state["count"]

            if count_state["state"] == IssueState.OPENED:
                summary.opened_count = count_state["count"]
            elif count_state["state"] == IssueState.CLOSED:
                summary.closed_count = count_state["count"]

        summary.time_spent = self._get_time_spent()
        summary.problems_count = self._get_problems_count()

        return summary

    def _get_counts_by_state(self) -> QuerySet:
        return (
            self._queryset.values("state")
            .annotate(count=Count("*"))
            .order_by()
        )

    def _get_time_spent(self) -> int:
        queryset = SpentTime.objects.filter(issues__isnull=False)

        filters_map = {
            "due_date": "date",
            "user": "user",
            "team": "user__teams",
            "project": "issues__project",
            "state": "issues__state",
            "milestone": "issues__milestone",
            "ticket": "issues__ticket",
        }

        for option, lookup in filters_map.items():
            option_value = self._options.get(option)
            if option_value:
                queryset = queryset.filter(**{lookup: option_value})

        return (
            queryset.aggregate(total_time_spent=Sum("time_spent"))[
                "total_time_spent"
            ]
            or 0
        )

    def _get_problems_count(self) -> int:
        queryset = annotate_issue_problems(self._queryset)
        queryset = filter_issue_problems(queryset)

        return queryset.count()


def get_issues_summary(queryset: QuerySet, **kwargs) -> IssuesSummary:
    """Get summary for issues."""
    return IssuesSummaryProvider(queryset, **kwargs).execute()
