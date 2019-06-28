from collections import namedtuple

from django.db.models import QuerySet

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
            time_spent=0,
            problems_count=0
        )

    def _get_issues_count(self) -> int:
        return self.queryset.count()


def get_issues_summary(queryset: QuerySet) -> IssuesSummary:
    provider = IssuesSummaryProvider(queryset)

    return provider.execute()
