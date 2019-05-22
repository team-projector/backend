from apps.development.models import Feature
from .calculator import FeatureMetrics, FeatureMetricsCalculator


def get_feature_metrics(feature: Feature) -> FeatureMetrics:
    return FeatureMetricsCalculator(feature).calculate()
