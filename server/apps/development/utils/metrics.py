from datetime import datetime
from typing import Iterable

from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db.models import IntegerField, Sum
from django.db.models.functions import Cast, TruncDay

from apps.development.models import Note
from apps.users.models import User


class Metric:
    start = None
    end = None
    time_spent = None
    time_estimate = None
    efficiency = None
    earnings = None


class BaseGrouper:
    pass


class DaysGrouper(BaseGrouper):
    pass


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
        return Note.objects.filter(user=self.user, created_at__range=(self.start, self.end)) \
            .annotate(spent=Cast(KeyTextTransform('spent', 'data'), IntegerField()),
                      # month=TruncMonth('created_at'),
                      day=TruncDay('created_at'),
                      # week=TruncWeek('created_at')
                      ) \
            .values('day') \
            .annotate(period_spent=Sum('spent')) \
            .order_by()
