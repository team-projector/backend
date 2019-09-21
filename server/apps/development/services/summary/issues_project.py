from datetime import datetime
from typing import List, Optional

from django.db.models import (
    QuerySet, Sum, Count, Case, When, Q, IntegerField, Value, F,
)
from django.db.models.functions import Coalesce

from apps.development.models import Project
from apps.development.models.issue import STATE_CLOSED


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
        summaries_qs = self._get_summaries_qs()

        summaries = {
            summary['project']: summary
            for summary in
            summaries_qs
        }

        total_issues_count = self._get_total_issues_count(summaries_qs)

        projects_qs = self._get_project_qs(summaries_qs)

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

    def _get_summaries_qs(self) -> QuerySet:
        return self.queryset.annotate(
            time_remains=Case(
                When(
                    Q(time_estimate__gt=F('total_time_spent')) &  # noqa:W504
                    ~Q(state=STATE_CLOSED),
                    then=F('time_estimate') - F('total_time_spent'),
                ),
                default=Value(0),
                output_field=IntegerField(),
            ),
        ).values(
            'project',
        ).annotate(
            issues_opened_count=Count('*'),
            total_time_remains=Coalesce(Sum('time_remains'), 0),
        ).order_by()

    def _get_total_issues_count(self, summaries_qs: QuerySet) -> int:
        return sum(
            item['issues_opened_count']
            for item in summaries_qs
        )

    def _get_project_qs(self, summaries_qs: QuerySet) -> list:
        project_ids = [
            item['project']
            for item in summaries_qs
        ]

        projects_qs = Project.objects.filter(id__in=project_ids)
        projects_qs = sorted(projects_qs, key=get_min_due_date)

        return projects_qs


def get_project_summaries(queryset: QuerySet,
                          order_by: str = None) -> List[IssuesProjectSummary]:
    provider = IssuesProjectSummaryProvider(
        queryset,
        order_by,
    )

    return provider.execute()
