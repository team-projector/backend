from datetime import date, timedelta
from typing import Iterable, List

from django.db.models import Avg, Count, F, FloatField, QuerySet, Sum
from django.db.models.functions import Cast, Coalesce, TruncWeek
from django.utils.timezone import make_aware

from apps.core.utils.date import begin_of_week, date2datetime
from apps.development.models.issue import Issue, STATE_CLOSED
from apps.payroll.models import SpentTime
from .base import ProgressMetricsCalculator, UserProgressMetrics

WEEK_STEP = timedelta(weeks=1)


class WeekMetricsCalculator(ProgressMetricsCalculator):
    def calculate(self) -> Iterable[UserProgressMetrics]:
        metrics = []

        spents = {
            spent['week']: spent
            for spent in self.get_spents()
        }

        for week in self._get_weeks():
            metric = UserProgressMetrics()
            metrics.append(metric)

            metric.start = week
            metric.end = week + timedelta(weeks=1)
            metric.planned_work_hours = self.user.daily_work_hours

            self._update_deadlines(metric)
            self._update_efficiency(metric)
            self._update_payrolls(metric)

            if week in spents:
                spent = spents[week]
                metric.time_spent = spent['period_spent']

        return metrics

    def modify_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.annotate(
            week=TruncWeek('date')
        ).values('week')

    def _update_deadlines(self, metric: UserProgressMetrics) -> None:
        issues_stats = Issue.objects.filter(
            user=self.user,
            due_date__gte=metric.start,
            due_date__lt=metric.end
        ).aggregate(
            issues_count=Count('*'),
            total_time_estimate=Coalesce(Sum('time_estimate'), 0)
        )

        metric.issues_count = issues_stats['issues_count']
        metric.time_estimate = issues_stats['total_time_estimate']

    def _update_efficiency(self, metric: UserProgressMetrics) -> None:
        issues_stats = Issue.objects.filter(
            user=self.user,
            closed_at__range=(
                make_aware(date2datetime(metric.start)),
                make_aware(date2datetime(metric.end))
            ),
            state=STATE_CLOSED,
            total_time_spent__gt=0,
            time_estimate__gt=0
        ).annotate(
            efficiency=Cast(F('time_estimate'), FloatField()) / Cast(F('total_time_spent'), FloatField())
        ).aggregate(
            avg_efficiency=Coalesce(Avg('efficiency'), 0)
        )

        metric.efficiency = issues_stats['avg_efficiency']

    def _update_payrolls(self, metric: UserProgressMetrics) -> None:
        data = SpentTime.objects.filter(
            user=self.user,
            date__gte=metric.start,
            date__lt=metric.end
        ).aggregate_payrolls()

        metric.payroll = data['total_payroll']
        metric.paid = data['total_paid']

    def _get_weeks(self) -> List[date]:
        ret: List[date] = []
        current = self.start

        while current <= self.end:
            ret.append(begin_of_week(current))
            current += WEEK_STEP

        return ret
