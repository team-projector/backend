from datetime import date
from typing import List, Optional

from django.db.models import QuerySet, Sum, Count

from apps.development.models import Team, Project, Milestone
from apps.development.models.issue import ISSUE_STATES
from apps.development.services.problems.issue import (
    annotate_issues_problems, filter_issues_problems
)
from apps.payroll.models import SpentTime
from apps.users.models import User
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
    def __init__(self,
                 queryset: QuerySet,
                 due_date: Optional[date],
                 user: Optional[User],
                 team: Optional[Team],
                 project: Optional[Project],
                 state: Optional[str],
                 milestone: Optional[Milestone]):
        self.queryset = queryset
        self.queryset = queryset
        self.due_date = due_date
        self.user = user
        self.team = team
        self.project = project
        self.state = state
        self.milestone = milestone

    def execute(self) -> IssuesSummary:
        summary = IssuesSummary()
        summary.queryset = self.queryset

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
        return self.queryset.values(
            'state'
        ).annotate(
            count=Count('*')
        ).order_by()

    def _get_time_spent(self) -> int:  # noqa: C901
        queryset = SpentTime.objects.filter(issues__isnull=False)

        if self.due_date:
            queryset = queryset.filter(date=self.due_date)

        if self.user:
            queryset = queryset.filter(user=self.user)

        if self.team:
            queryset = queryset.filter(user__teams=self.team)

        if self.project:
            queryset = queryset.filter(issues__project=self.project)

        if self.state:
            queryset = queryset.filter(issues__state=self.state)

        if self.milestone:
            queryset = queryset.filter(issues__milestone=self.milestone)

        return queryset.aggregate(
            total_time_spent=Sum('time_spent')
        )['total_time_spent'] or 0

    def _get_problems_count(self) -> int:
        queryset = annotate_issues_problems(self.queryset)
        queryset = filter_issues_problems(queryset)

        return queryset.count()


def get_issues_summary(queryset: QuerySet,
                       due_date: Optional[date],
                       user: Optional[User],
                       team: Optional[Team],
                       project: Optional[Project],
                       state: Optional[str],
                       milestone: Optional[Milestone]) -> IssuesSummary:
    return IssuesSummaryProvider(
        queryset,
        due_date,
        user,
        team,
        project,
        state,
        milestone
    ).execute()
