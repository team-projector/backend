from typing import Optional, Type, Union

from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, Value, QuerySet
from django.db.models.functions import Coalesce

from apps.development.models import Issue, MergeRequest, Project, Team
from apps.development.services.summary.issues import (
    IssuesSummary, get_issues_summary
)
from apps.development.services.summary.merge_requests import (
    MergeRequestsSummary, get_merge_requests_summary
)
from apps.users.models import User


class IssuesSpentTimesSummary(IssuesSummary):
    spent: int = 0


class MergeRequestsSpentTimesSummary(MergeRequestsSummary):
    spent: int = 0


class SpentTimesSummary:
    spent: int = 0
    issues: IssuesSpentTimesSummary
    merge_requests: MergeRequestsSpentTimesSummary


class SpentTimesSummaryProvider:
    def __init__(self,
                 queryset: QuerySet,
                 project: Optional[Project],
                 team: Optional[Team],
                 user: Optional[User]):
        self.queryset = queryset
        self.project = project
        self.team = team
        self.user = user

    def execute(self) -> SpentTimesSummary:
        summary = SpentTimesSummary()

        summary.issues = IssuesSpentTimesSummary()
        summary.issues.__dict__ \
            = self._get_issues_summary().__dict__

        summary.merge_requests = MergeRequestsSpentTimesSummary()
        summary.merge_requests.__dict__ \
            = self._get_merge_requests_summary().__dict__

        for item in self._get_time_spent():
            if self._is_model_class(item['content_type'], Issue):
                summary.issues.spent = item['spent']
                summary.spent += item['spent']
            elif self._is_model_class(item['content_type'], MergeRequest):
                summary.merge_requests.spent = item['spent']
                summary.spent += item['spent']

        return summary

    def _get_issues_summary(self) -> IssuesSummary:
        return get_issues_summary(
            Issue.objects.filter(
                id__in=self.queryset.values_list(
                    'issues__id', flat=True
                )
            ),
            None,
            self.user,
            self.team,
            self.project,
            None
        )

    def _get_merge_requests_summary(self) -> MergeRequestsSummary:
        return get_merge_requests_summary(
            MergeRequest.objects.filter(
                id__in=self.queryset.values_list(
                    'mergerequests__id', flat=True
                )
            ),
            self.project,
            self.team,
            self.user
        )

    def _get_time_spent(self) -> QuerySet:
        return self.queryset.values('content_type').annotate(
            spent=Coalesce(Sum('time_spent'), Value(0))
        ).order_by()

    @staticmethod
    def _is_model_class(id: int,
                        model_class: Union[
                            Type[Issue], Type[MergeRequest]
                        ]) -> bool:
        return ContentType.objects.get_for_id(id).model_class() == model_class


def get_spent_times_summary(queryset: QuerySet,
                            project: Optional[Project],
                            team: Optional[Team],
                            user: Optional[User]) -> SpentTimesSummary:
    provider = SpentTimesSummaryProvider(
        queryset,
        project,
        team,
        user
    )

    return provider.execute()
