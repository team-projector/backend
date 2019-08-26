from django.db.models import QuerySet


class IssuesSpentTimesSummary:
    spent: int = 0
    closed_spent: int = 0
    opened_spent: int = 0

    def __init__(self,
                 spent=0,
                 closed_spent=0,
                 opened_spent=0) -> None:
        self.spent = spent
        self.closed_spent = closed_spent
        self.opened_spent = opened_spent


class MergeRequestsSpentTimesSummary:
    spent: int = 0
    closed_spent: int = 0
    opened_spent: int = 0
    merged_spent: int = 0

    def __init__(self,
                 spent=0,
                 closed_spent=0,
                 opened_spent=0,
                 merged_spent=0) -> None:
        self.spent = spent
        self.closed_spent = closed_spent
        self.opened_spent = opened_spent
        self.merged_spent = merged_spent


class SpentTimesSummary:
    issues: IssuesSpentTimesSummary
    merge_requests: MergeRequestsSpentTimesSummary

    def __init__(self,
                 issues: IssuesSpentTimesSummary,
                 merge_requests: MergeRequestsSpentTimesSummary):
        self.issues = issues
        self.merge_requests = merge_requests

    @property
    def spent(self) -> int:
        return self.issues.spent + self.merge_requests.spent

    @property
    def opened_spent(self) -> int:
        return self.issues.opened_spent + self.merge_requests.opened_spent


class SpentTimesSummaryProvider:
    def __init__(self,
                 queryset: QuerySet):
        self.queryset = queryset

    def execute(self) -> SpentTimesSummary:
        spent_summaries = self.queryset.summaries()

        issues_summaries = IssuesSpentTimesSummary(
            spent=spent_summaries['total_issues'],
            opened_spent=spent_summaries['opened_issues'],
            closed_spent=spent_summaries['closed_issues']
        )

        merges_summaries = MergeRequestsSpentTimesSummary(
            spent=spent_summaries['total_merges'],
            opened_spent=spent_summaries['opened_merges'],
            closed_spent=spent_summaries['closed_merges'],
            merged_spent=spent_summaries['merged_merges']
        )

        return SpentTimesSummary(
            issues_summaries,
            merges_summaries
        )


def get_spent_times_summary(queryset: QuerySet) -> SpentTimesSummary:
    return SpentTimesSummaryProvider(
        queryset
    ).execute()
