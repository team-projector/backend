from apps.development.models import Feature
from .provider import FeatureMetrics, FeatureMetricsProvider


def get_feature_metrics(feature: Feature) -> FeatureMetrics:
    return FeatureMetricsProvider(feature).get_metrics()
