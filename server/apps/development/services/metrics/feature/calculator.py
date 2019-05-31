from django.db.models import QuerySet

from apps.development.models import Feature
from ..calculator import IssuesContainerCalculator, IssuesContainerMetrics


class FeatureMetrics(IssuesContainerMetrics):
    pass


class FeatureMetricsCalculator(IssuesContainerCalculator):
    def __init__(self, feature: Feature):
        self.feature = feature

    def filter_issues(self, queryset: QuerySet) -> QuerySet:
        return queryset.filter(feature=self.feature)

    def calculate(self) -> FeatureMetrics:
        metrics = FeatureMetrics()

        self.fill_issues_metrics(metrics)

        return metrics
