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

KEY_STATE = "state"


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
            summary.count += count_state["count"]

            if count_state[KEY_STATE] == IssueState.OPENED:
                summary.opened_count = count_state["count"]
            elif count_state[KEY_STATE] == IssueState.CLOSED:
                summary.closed_count = count_state["count"]

        summary.time_spent = self._get_time_spent()
        summary.problems_count = self._get_problems_count()

        return summary

    def _get_counts_by_state(self) -> QuerySet:
        """
        Get counts by state.

        :rtype: QuerySet
        """
        return (
            self._queryset.values(KEY_STATE)
            .annotate(count=Count("*"))
            .order_by()
        )

    def _get_time_spent(self) -> int:
        """
        Get time spent.

        :rtype: int
        """
        queryset = SpentTime.objects.filter(issues__isnull=False)

        filters_map = {
            "due_date": "date",
            "team": "user__teams",
            "project": "issues__project",
            "state": "issues__state",
            "milestone": "issues__milestone",
            "ticket": "issues__ticket",
            "craeted_by": "issues__author",
            "assigned_to": "issues__user",
            "participated_by": "issues__participants",
        }

        for option, lookup in filters_map.items():
            option_value = self._options.get(option)
            if option_value:
                queryset = queryset.filter(**{lookup: option_value})

        queryset = self._filter_spents_by_user(queryset)

        return (
            queryset.aggregate(total_time_spent=Sum("time_spent"))[
                "total_time_spent"
            ]
            or 0
        )

    def _filter_spents_by_user(self, queryset: QuerySet) -> QuerySet:
        """Filter queryset with spents by user."""
        users = []
        for user_field in ("craeted_by", "assigned_to", "participated_by"):
            user_value = self._options.get(user_field)
            if user_value:
                users.append(user_value)

        if users:
            queryset = queryset.filter(user__in=users)

        return queryset

    def _get_problems_count(self) -> int:
        """
        Get problems count.

        :rtype: int
        """
        queryset = annotate_issue_problems(self._queryset)
        queryset = filter_issue_problems(queryset)

        return queryset.count()


def get_issues_summary(queryset: QuerySet, **kwargs) -> IssuesSummary:
    """Get summary for issues."""
    return IssuesSummaryProvider(queryset, **kwargs).execute()
