from django.db.models import QuerySet

from apps.development.models import Feature
from ..provider import IssuesContainerMetricsProvider, IssuesContainerMetrics


class FeatureMetrics(IssuesContainerMetrics):
    pass


class FeatureMetricsProvider(IssuesContainerMetricsProvider):
    def __init__(self, feature: Feature):
        self.feature = feature

    def filter_issues(self,
                      queryset: QuerySet) -> QuerySet:
        return queryset.filter(feature=self.feature)

    def get_metrics(self) -> FeatureMetrics:
        metrics = FeatureMetrics()

        self.fill_issues_metrics(metrics)

        return metrics
