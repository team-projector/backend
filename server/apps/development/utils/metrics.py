from datetime import datetime
from typing import Iterable

from django.db.models import Sum
from django.db.models.functions import TruncDay

from apps.payroll.models import SpentTime
from apps.users.models import User


class Metric:
    start = None
    end = None
    time_spent = None
    time_estimate = None
    efficiency = None
    earnings = None


class BaseGrouper:
    group = None

    def setup_queryset(self, queryset):
        raise NotImplementedError


class DaysGrouper(BaseGrouper):
    group = 'day'


class WeekGrouper(BaseGrouper):
    group = 'week'


class MetricsCalculator:
    def __init__(self, user: User, start: datetime, end: datetime, group: str):
        self.user = user
        self.start = start
        self.end = end
        self.group = group

    def calculate(self) -> Iterable[Metric]:
        metrics = []

        for spend in self._get_spends():
            metric = Metric()
            metric.start = spend['day'].date()
            metric.end = spend['day'].date()
            metric.time_spent = spend['period_spent']

            metrics.append(metric)

        return sorted(metrics, key=lambda x: x.start)

    def _get_spends(self):
        return SpentTime.objects.filter(employee=self.user, date__range=(self.start, self.end)) \
            .annotate(day=TruncDay('date')) \
            .values('day') \
            .annotate(period_spent=Sum('time_spent')) \
            .order_by()

    @staticmethod
    def _get_grouper(group: str) -> BaseGrouper:
        return next(grouper_class()
                    for grouper_class in BaseGrouper.__subclasses__()
                    if grouper_class.group == group)
