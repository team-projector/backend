from django.db.models import Count, Sum
from django.db.models.functions import Coalesce

from apps.development.models import Milestone, Issue


class MilestoneMetrics:
    time_estimate: int = 0
    time_spent: int = 0
    time_remains: int = 0
    issues_count: int = 0
    efficiency: float = 0.0
    salary: float = 0.0


class ProjectMilestoneMetricsCalculator:
    def __init__(self, milestone: Milestone):
        self.milestone = milestone

    def calculate(self) -> MilestoneMetrics:
        metrics = MilestoneMetrics()

        stat = Issue.objects.filter(
            milestone=self.milestone.id,
        ).aggregate(
            issues_count=Count('*'),
            time_estimate=Coalesce(Sum('time_estimate'), 0),
            time_spent=Coalesce(Sum('total_time_spent'), 0)
        )
        if stat:
            metrics.time_estimate = stat['time_estimate']
            metrics.time_spent = stat['time_spent']
            metrics.time_remains = stat['time_estimate'] - stat['time_spent']
            metrics.issues_count = stat['issues_count']

        return metrics
