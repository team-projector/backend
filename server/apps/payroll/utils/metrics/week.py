from datetime import date, timedelta
from typing import Iterable, List

from django.db.models import Count, Sum
from django.db.models.functions import TruncWeek

from apps.core.utils.date import begin_of_week
from apps.development.models import Issue
from .base import Metric, MetricsCalculator

WEEK_STEP = timedelta(weeks=1)


class WeekMetricsCalculator(MetricsCalculator):
    def calculate(self) -> Iterable[Metric]:
        metrics = []

        spents = {
            spent['week']: spent
            for spent in self.get_spents()
        }

        for week in self._get_weeks():
            metric = Metric()
            metrics.append(metric)

            metric.start = week
            metric.end = week + timedelta(weeks=1)

            deadline_stats = Issue.objects.filter(employee=self.user, due_date__range=(metric.start, metric.end)) \
                .exclude(state='closed') \
                .aggregate(issues_count=Count('*'),
                           total_time_estimate=Sum('time_estimate'))

            metric.issues = deadline_stats['issues_count']
            metric.time_estimate = deadline_stats['total_time_estimate'] or 0

            if week in spents:
                spent = spents[week]
                metric.time_spent = spent['period_spent']

        return metrics

    def modify_queryset(self, queryset):
        return queryset.annotate(week=TruncWeek('date')).values('week')

    def _get_weeks(self) -> List[date]:
        ret: List[date] = []
        current = self.start

        while current <= self.end:
            ret.append(begin_of_week(current))
            current += WEEK_STEP

        return ret
