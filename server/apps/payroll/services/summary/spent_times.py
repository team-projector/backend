from django.db.models import Sum, Value, QuerySet
from django.db.models.functions import Coalesce

from apps.development.models import MergeRequest
from apps.development.models.issue import STATE_CLOSED, STATE_OPENED


class IssuesSpentTimesSummary:
    spent: int = 0
    closed_spent: int = 0
    opened_spent: int = 0


class MergeRequestsSpentTimesSummary:
    spent: int = 0
    closed_spent: int = 0
    opened_spent: int = 0
    merged_spent: int = 0


class SpentTimesSummary:
    spent: int = 0
    issues: IssuesSpentTimesSummary
    merge_requests: MergeRequestsSpentTimesSummary


class SpentTimesSummaryProvider:
    def __init__(self,
                 queryset: QuerySet):
        self.queryset = queryset

    def execute(self) -> SpentTimesSummary:
        summary = SpentTimesSummary()

        summary.issues = IssuesSpentTimesSummary()
        self._calculate_issues(summary.issues)

        summary.merge_requests = MergeRequestsSpentTimesSummary()
        self._calculate_merge_requests(summary.merge_requests)

        summary.spent = summary.issues.spent + summary.merge_requests.spent

        return summary

    def _get_issues_spent(self) -> QuerySet:
        return self.queryset.filter(
            issues__isnull=False
        ).values(
            'issues__state'
        ).annotate(
            spent=Coalesce(Sum('time_spent'), Value(0))
        ).order_by()

    def _get_merge_requests_spent(self) -> QuerySet:
        return self.queryset.filter(
            mergerequests__isnull=False
        ).values(
            'mergerequests__state'
        ).annotate(
            spent=Coalesce(Sum('time_spent'), Value(0))
        ).order_by()

    def _calculate_issues(self, issues) -> None:
        for item in self._get_issues_spent():
            if item['issues__state'] == STATE_OPENED:
                issues.opened_spent = item['spent']
                issues.spent += item['spent']
            elif item['issues__state'] == STATE_CLOSED:
                issues.closed_spent = item['spent']
                issues.spent += item['spent']
            else:
                issues.spent += item['spent']

    def _calculate_merge_requests(self, merge_requests) -> None:
        for item in self._get_merge_requests_spent():
            if item['mergerequests__state'] == MergeRequest.STATE.opened:
                merge_requests.opened_spent = item['spent']
                merge_requests.spent += item['spent']
            elif item['mergerequests__state'] == MergeRequest.STATE.closed:
                merge_requests.closed_spent = item['spent']
                merge_requests.spent += item['spent']
            elif item['mergerequests__state'] == MergeRequest.STATE.merged:
                merge_requests.merged_spent = item['spent']
                merge_requests.spent += item['spent']
            else:
                merge_requests.spent += item['spent']


def get_spent_times_summary(queryset: QuerySet) -> SpentTimesSummary:
    return SpentTimesSummaryProvider(queryset).execute()
