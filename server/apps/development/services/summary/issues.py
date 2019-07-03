from collections import namedtuple
from datetime import date

from django.db.models import QuerySet, Sum

from apps.development.models import Team
from apps.development.services.problems.issues import (
    annotate_issues_problems, filter_issues_problems
)
from apps.payroll.models import SpentTime
from apps.users.models import User

IssuesSummary = namedtuple(
    'IssuesSummary', [
        'issues_count',
        'time_spent',
        'problems_count'
    ])


class IssuesSummaryProvider:
    def __init__(self,
                 queryset: QuerySet,
                 due_date: date,
                 user: User,
                 team: Team):
        self.queryset = queryset
        self.due_date = due_date
        self.user = user
        self.team = team

    def execute(self) -> IssuesSummary:
        return IssuesSummary(
            issues_count=self._get_issues_count(),
            time_spent=self._get_time_spent(),
            problems_count=self._get_problems_count()
        )

    def _get_issues_count(self) -> int:
        return self.queryset.count()

    def _get_time_spent(self) -> int:
        queryset = SpentTime.objects.all()

        if self.due_date:
            queryset = queryset.filter(date=self.due_date)

        if self.user:
            queryset = queryset.filter(user=self.user)

        if self.team:
            queryset = queryset.filter(user__teams=self.team)

        return queryset.aggregate(
            total_time_spent=Sum('time_spent')
        )['total_time_spent'] or 0

    def _get_problems_count(self) -> int:
        queryset = annotate_issues_problems(self.queryset)
        queryset = filter_issues_problems(queryset)

        return queryset.count()


def get_issues_summary(queryset: QuerySet,
                       due_date: date,
                       user: User,
                       team: Team) -> IssuesSummary:
    provider = IssuesSummaryProvider(
        queryset,
        due_date,
        user,
        team
    )

    return provider.execute()
