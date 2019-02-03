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


class BaseMetricsCalculator:
    def __init__(self, user: User, start: datetime, end: datetime):
        self.user = user
        self.start = start
        self.end = end

    def calculate(self) -> Iterable[Metric]:
        raise NotImplementedError

    def get_spents(self):
        queryset = SpentTime.objects.filter(employee=self.user,
                                            date__range=(
                                                make_aware(date2datetime(self.start)),
                                                make_aware(date2datetime(self.end))
                                            ))
        queryset = self.modify_queryset(queryset)

        return queryset.annotate(period_spent=Sum('time_spent')).order_by()

    def modify_queryset(self, queryset):
        raise NotImplementedError


class DayMetricsCalculator(BaseMetricsCalculator):
    def calculate(self) -> Iterable[Metric]:
        metrics = []

        # step = timedelta(days=1)
        #
        # spents = list(self._get_spents())
        #
        # current = self.start
        # while current <= self.end:
        #     metric = Metric()
        #
        #     spent = next(i for i in spents if i['day'].date() == current)
        #     metric.start, metric.end = self.grouper.get_period(spent)
        #     if spent
        #
        #     metric.time_spent = spent['period_spent']
        #
        #     metrics.append(metric)
        #
        #     current += step

        for spent in self.get_spents():
            metric = Metric()
            metric.start = metric.end = spent['day'].date()
            metric.time_spent = spent['period_spent']

            metrics.append(metric)

        return sorted(metrics, key=lambda x: x.start)

    def modify_queryset(self, queryset):
        return queryset.annotate(day=TruncDay('date')).values('day')


def create_calculator(user: User, start: datetime, end: datetime, group: str):
    if group == 'day':
        return DayMetricsCalculator(user, start, end)
