from datetime import date, datetime
from typing import List, Optional

from django.db.models import (
    QuerySet, Sum, Count, Case, When, Q, IntegerField, Value, F
)
from django.db.models.functions import Coalesce

from apps.development.models import Team, Project, Milestone
from apps.development.models.issue import STATE_CLOSED, STATE_OPENED
from apps.development.services.problems.issue import (
    annotate_issues_problems, filter_issues_problems
)
from apps.payroll.models import SpentTime
from apps.users.models import User


def get_min_due_date(project):
    def get_date(milestone):
        return getattr(milestone, 'due_date', None) or datetime.max.date()

    sorted_milestones = sorted(project.active_milestones, key=get_date)
    if sorted_milestones:
        return sorted_milestones[0].due_date or datetime.max.date()

    return datetime.max.date()


class ProjectIssuesSummary:
    opened_count: int = 0
    percentage: float = 0.0
    remains: int = 0


class IssuesProjectSummary:
    project: Project
    issues: ProjectIssuesSummary
    order_by: str


class IssuesProjectSummaryProvider:
    def __init__(self,
                 queryset: QuerySet,
                 order_by: Optional[str]):
        self.queryset = queryset
        self.order_by = order_by

    def execute(self) -> List[IssuesProjectSummary]:
        summaries_qs = self.queryset.annotate(
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

        summaries = {
            summary['project']: summary
            for summary in
            summaries_qs
        }

        total_issues_count = sum(
            [
                item['issues_opened_count']
                for item in summaries_qs
            ]
        )

        project_ids = [
            item['project']
            for item in summaries_qs
        ]

        projects_qs = Project.objects.filter(id__in=project_ids)
        projects_qs = sorted(projects_qs, key=get_min_due_date)

        ret = []

        for p in projects_qs:
            summary = IssuesProjectSummary()
            summary.project = p

            issues_summary = ProjectIssuesSummary()
            issues_summary.opened_count = summaries[p.id]['issues_opened_count']
            issues_summary.remains = summaries[p.id]['total_time_remains']
            issues_summary.percentage = (
                issues_summary.opened_count / total_issues_count
            )

            summary.issues = issues_summary

            ret.append(summary)

        return ret


class TeamIssuesSummary:
    opened_count: int = 0
    percentage: float = 0.0
    remains: int = 0


class IssuesTeamSummary:
    team: Team
    issues: TeamIssuesSummary
    order_by: str


class IssuesTeamSummaryProvider:
    def __init__(self,
                 queryset: QuerySet,
                 order_by: Optional[str]):
        self.queryset = queryset
        self.order_by = order_by

    def execute(self) -> List[IssuesProjectSummary]:
        summaries_qs = self.queryset.annotate(
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
            'user__teams'
        ).annotate(
            issues_opened_count=Count('*'),
            total_time_remains=Coalesce(Sum('time_remains'), 0)
        ).order_by()

        summaries = {
            summary['user__teams']: summary
            for summary in
            summaries_qs
        }

        total_issues_count = sum(
            [
                item['issues_opened_count']
                for item in summaries_qs
            ]
        )

        team_ids = [
            item['user__teams']
            for item in summaries_qs
        ]

        team_qs = Team.objects.filter(id__in=team_ids)

        ret = []

        for t in team_qs:
            summary = IssuesTeamSummary()
            summary.team = t

            issues_summary = TeamIssuesSummary()
            issues_summary.opened_count = summaries[t.id]['issues_opened_count']
            issues_summary.remains = summaries[t.id]['total_time_remains']
            issues_summary.percentage = (
                issues_summary.opened_count / total_issues_count
            )

            summary.issues = issues_summary

            ret.append(summary)

        return ret


class IssuesSummary:
    count: int = 0
    opened_count: int = 0
    closed_count: int = 0
    time_spent: int = 0
    problems_count: int = 0
    projects: List[IssuesProjectSummary] = []

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

            if item['state'] == STATE_OPENED:
                summary.opened_count = item['count']
            elif item['state'] == STATE_CLOSED:
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

    def _get_time_spent(self) -> int:
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


def get_project_summaries(queryset: QuerySet,
                          order_by: str = None) -> List[IssuesProjectSummary]:
    provider = IssuesProjectSummaryProvider(
        queryset,
        order_by
    )

    return provider.execute()


def get_team_summaries(queryset: QuerySet,
                       order_by: str = None) -> List[IssuesProjectSummary]:
    provider = IssuesTeamSummaryProvider(
        queryset,
        order_by
    )

    return provider.execute()
