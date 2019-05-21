from apps.development.models import Milestone
from .calculator import MilestoneMetrics, MilestoneMetricsCalculator


def get_milestone_metrics(milestone: Milestone) -> MilestoneMetrics:
    return MilestoneMetricsCalculator(milestone).calculate()
