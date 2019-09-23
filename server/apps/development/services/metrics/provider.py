from django.db.models import Count, Q, QuerySet, Sum
from django.db.models.functions import Coalesce

from apps.development.models import Issue
from apps.development.models.issue import ISSUE_STATES


class IssuesContainerMetrics:
    time_estimate: int = 0
    time_spent: int = 0
    time_remains: int = 0
    issues_count: int = 0
    issues_closed_count: int = 0
    issues_opened_count: int = 0
    efficiency: float = 0.0


class IssuesContainerMetricsProvider:
    def fill_issues_metrics(self, metrics: IssuesContainerMetrics) -> None:
        issues = Issue.objects.all()
        issues = self.filter_issues(issues)

        stats = issues.aggregate(
            time_estimate=Coalesce(Sum('time_estimate'), 0),
            time_spent=Coalesce(Sum('total_time_spent'), 0),
            issues_closed_count=Coalesce(
                Count('id', filter=Q(state=ISSUE_STATES.closed)), 0,
            ),
            issues_opened_count=Coalesce(
                Count('id', filter=Q(state=ISSUE_STATES.opened)), 0,
            ),
            issues_count=Count('*'),
        )

        if stats:
            metrics.time_estimate = stats['time_estimate']
            metrics.time_remains = stats['time_estimate'] - stats['time_spent']

            if stats['time_spent']:
                metrics.efficiency = stats['time_estimate'] / stats[
                    'time_spent']

            metrics.time_spent = stats['time_spent']

            metrics.issues_closed_count = stats['issues_closed_count']
            metrics.issues_opened_count = stats['issues_opened_count']
            metrics.issues_count = stats['issues_count']

    def filter_issues(self, queryset: QuerySet) -> QuerySet:
        raise NotImplementedError
