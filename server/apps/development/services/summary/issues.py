from datetime import date
from typing import List, Optional

from django.db.models import (
    QuerySet, Sum, Count, Case, When, Q, IntegerField, Value, F
)
from django.db.models.functions import Coalesce

from apps.development.models import Team, Project
from apps.development.models.issue import STATE_CLOSED
from apps.development.services.problems.issue import (
    annotate_issues_problems, filter_issues_problems
)
from apps.payroll.models import SpentTime
from apps.users.models import User


class ProjectIssuesSummary:
    opened_count: int = 0
    percentage: float = 0.0
    remains: int = 0


class IssuesProjectSummary:
    project: Project
    issues: ProjectIssuesSummary


class IssuesSummary:
    issues_count: int = 0
    time_spent: int = 0
    problems_count: int = 0
    projects: List[IssuesProjectSummary] = []


class IssuesSummaryProvider:
    def __init__(self,
                 queryset: QuerySet,
                 due_date: Optional[date],
                 user: Optional[User],
                 team: Optional[Team]):
        self.queryset = queryset
        self.due_date = due_date
        self.user = user
        self.team = team

    def execute(self) -> IssuesSummary:
        summary = IssuesSummary()
        summary.issues_count = self._get_issues_count()
        summary.time_spent = self._get_time_spent()
        summary.problems_count = self._get_problems_count()

        summary.projects = self._get_projects_summary()

        return summary

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

    def _get_projects_summary(self) -> List[IssuesProjectSummary]:
        queryset = self.queryset.annotate(
            time_remains=Case(
                When(
                    Q(time_estimate__gt=F('total_time_spent')) &  # noqa:W504
                    ~Q(state=STATE_CLOSED),
                    then=F('time_estimate') - F('total_time_spent')
                ),
                default=Value(0),
                output_field=IntegerField()
            ),
        ).values(
            'project'
        ).annotate(
            issues_opened_count=Count('*'),
            total_time_remains=Coalesce(Sum('time_remains'), 0)
        ).order_by()

        projects = {
            project.id: project
            for project in
            Project.objects.filter(
                id__in=[
                    item['project']
                    for item in queryset
                ])
        }

        total_issues_count = sum(
            [
                item['issues_opened_count']
                for item in queryset
            ]
        )

        summaries = []

        for project_summary in queryset:
            summary = IssuesProjectSummary()
            summary.project = projects[project_summary['project']]

            issues_summary = ProjectIssuesSummary()
            issues_summary.opened_count = project_summary['issues_opened_count']
            issues_summary.remains = project_summary['total_time_remains']
            issues_summary.percentage = (issues_summary.opened_count /
                                         total_issues_count)

            summary.issues = issues_summary

            summaries.append(summary)

        return summaries


def get_issues_summary(queryset: QuerySet,
                       due_date: Optional[date],
                       user: Optional[User],
                       team: Optional[Team]) -> IssuesSummary:
    provider = IssuesSummaryProvider(
        queryset,
        due_date,
        user,
        team
    )

    return provider.execute()
