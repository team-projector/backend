from django.db.models import QuerySet, Count

from apps.development.models import MergeRequest


class MergeRequestsSummary:
    count: int = 0
    opened_count: int = 0
    closed_count: int = 0
    merged_count: int = 0


class MergeRequestsSummaryProvider:
    def __init__(self, queryset: QuerySet):
        self.queryset = queryset

    def execute(self) -> MergeRequestsSummary:
        summary = MergeRequestsSummary()

        for item in self._get_counts_by_state():
            if item['state'] == MergeRequest.STATE.opened:
                summary.opened_count = item['count']
                summary.count += item['count']
            elif item['state'] == MergeRequest.STATE.closed:
                summary.closed_count = item['count']
                summary.count += item['count']
            elif item['state'] == MergeRequest.STATE.merged:
                summary.merged_count = item['count']
                summary.count += item['count']
            else:
                summary.count += item['count']

        return summary

    def _get_counts_by_state(self) -> QuerySet:
        return self.queryset.values(
            'state'
        ).annotate(
            count=Count('*')
        ).order_by()


def get_merge_requests_summary(queryset: QuerySet) -> MergeRequestsSummary:
    return MergeRequestsSummaryProvider(queryset).execute()
