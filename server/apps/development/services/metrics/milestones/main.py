from django.db.models import Count, Sum, Q
from django.db.models.functions import Coalesce

from apps.development.models import Milestone, Issue
from apps.development.models.issue import STATE_CLOSED, STATE_OPENED


class MilestoneMetrics:
    budget_remains: int = 0
    efficiency: float = 0.0
    issues_closed_count: int = 0
    issues_opened_count: int = 0
    profit: int = 0
    salary: float = 0.0
    time_estimate: int = 0
    time_remains: int = 0
    time_spent: int = 0


class MilestoneMetricsCalculator:
    def __init__(self, milestone: Milestone):
        self.milestone = milestone

    def calculate(self):
        metrics = MilestoneMetrics()

        stat = Issue.objects.filter(
            milestone=self.milestone.id,
        ).aggregate(
            time_estimate=Coalesce(Sum('time_estimate'), 0),
            time_spent=Coalesce(Sum('total_time_spent'), 0),
            issues_closed_count=Coalesce(Count('id', filter=Q(state=STATE_CLOSED)), 0),
            issues_opened_count=Coalesce(Count('id', filter=Q(state=STATE_OPENED)), 0)
        )

        if not stat:
            return

        metrics.issues_closed_count = stat['issues_closed_count']
        metrics.issues_opened_count = stat['issues_opened_count']
        metrics.time_estimate = stat['time_estimate']
        metrics.time_remains = stat['time_estimate'] - stat['time_spent']
        metrics.time_spent = stat['time_spent']

        return metrics
