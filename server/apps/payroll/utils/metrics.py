from datetime import datetime
from typing import Iterable

from django.db.models import Sum
from django.db.models.functions import TruncDay
from django.utils.timezone import make_aware

from apps.core.utils.date import date2datetime
from apps.payroll.models import SpentTime
from apps.users.models import User


class Metric:
    start = None
    end = None
    time_spent = None
    loading = None
    efficiency = None
    earnings = None


class BaseGrouper:
    group = None

    def modify_queryset(self, queryset):
        raise NotImplementedError

    def get_period(self, spend):
        raise NotImplementedError


class DaysGrouper(BaseGrouper):
    group = 'day'

    def modify_queryset(self, queryset):
        return queryset.annotate(day=TruncDay('date')).values('day')

    def get_period(self, spend):
        return spend['day'].date(), spend['day'].date()


class WeekGrouper(BaseGrouper):
    group = 'week'


class MetricsCalculator:
    def __init__(self, user: User, start: datetime, end: datetime, group: str):
        self.user = user
        self.start = start
        self.end = end
        self.grouper = self._get_grouper(group)

    def calculate(self) -> Iterable[Metric]:
        metrics = []

        for spend in self._get_spends():
            metric = Metric()
            metric.start, metric.end = self.grouper.get_period(spend)
            metric.time_spent = spend['period_spent']

            metrics.append(metric)

        return sorted(metrics, key=lambda x: x.start)

    def _get_spends(self):
        queryset = SpentTime.objects.filter(employee=self.user,
                                            date__range=(
                                                make_aware(date2datetime(self.start)),
                                                make_aware(date2datetime(self.end))
                                            ))
        queryset = self.grouper.modify_queryset(queryset)

        return queryset.annotate(period_spent=Sum('time_spent')).order_by()

    @staticmethod
    def _get_grouper(group: str) -> BaseGrouper:
        return next(grouper_class()
                    for grouper_class in BaseGrouper.__subclasses__()
                    if grouper_class.group == group)
