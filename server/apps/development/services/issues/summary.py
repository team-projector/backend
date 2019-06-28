from collections import namedtuple

from django.db.models import QuerySet, Sum

IssuesSummary = namedtuple(
    'IssuesSummary', [
        'issues_count',
        'time_spent',
        'problems_count'
    ])


class IssuesSummaryProvider:
    def __init__(self, queryset: QuerySet):
        self.queryset = queryset

    def execute(self) -> IssuesSummary:
        return IssuesSummary(
            issues_count=self._get_issues_count(),
            time_spent=self._get_time_spent(),
            problems_count=self._get_problems_count()
        )

    def _get_issues_count(self) -> int:
        return self.queryset.count()

    def _get_time_spent(self) -> int:
        return self.queryset.aggregate(
            total_spent=Sum('total_time_spent')
        )['total_spent']

    def _get_problems_count(self) -> int:
        return 0


def get_issues_summary(queryset: QuerySet) -> IssuesSummary:
    provider = IssuesSummaryProvider(queryset)

    return provider.execute()
