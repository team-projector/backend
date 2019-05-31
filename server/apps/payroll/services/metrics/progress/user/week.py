from datetime import date, timedelta
from typing import Iterable, List

from django.db.models import Count, F, FloatField, QuerySet, Sum
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

        time_spents = {
            spent['week']: spent
            for spent in self.get_time_spents()
        }

        deadline_stats = self._get_deadlines_stats()
        efficiency_stats = self._get_efficiency_stats()
        payrolls_stats = self._get_payrolls_stats()

        for week in self._get_weeks():
            metric = UserProgressMetrics()
            metrics.append(metric)

            metric.start = week
            metric.end = week + timedelta(weeks=1)
            metric.planned_work_hours = self.user.daily_work_hours

            if week in deadline_stats:
                stats = deadline_stats[week]
                metric.issues_count = stats['issues_count']
                metric.time_estimate = stats['total_time_estimate']

            if week in efficiency_stats:
                stats = efficiency_stats[week]
                metric.efficiency = stats['avg_efficiency']

            if week in payrolls_stats:
                stats = payrolls_stats[week]
                metric.payroll = stats['total_payroll']
                metric.paid = stats['total_paid']

            if week in time_spents:
                spent = time_spents[week]
                metric.time_spent = spent['period_spent']

        return metrics

    def modify_time_spents_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.annotate(
            week=TruncWeek('date')
        ).values('week')

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

    def _get_deadlines_stats(self) -> dict:
        queryset = Issue.objects.annotate(
            week=TruncWeek('due_date'),
        ).filter(
            user=self.user,
            due_date__gte=self.start,
            due_date__lt=self.end,
            week__isnull=False
        ).values(
            'week'
        ).annotate(
            issues_count=Count('*'),
            total_time_estimate=Coalesce(Sum('time_estimate'), 0)
        ).order_by()

        return {
            stats['week']: stats
            for stats in queryset
        }

    def _get_efficiency_stats(self) -> dict:
        queryset = Issue.objects.annotate(
            week=TruncWeek('due_date')
        ).filter(
            user=self.user,
            closed_at__range=(
                make_aware(date2datetime(self.start)),
                make_aware(date2datetime(self.end))
            ),
            state=STATE_CLOSED,
            total_time_spent__gt=0,
            time_estimate__gt=0,
            week__isnull=False
        ).values(
            'week'
        ).annotate(
            avg_efficiency=Coalesce(
                Cast(Sum(F('time_estimate')), FloatField()) / Cast(Sum(F('total_time_spent')), FloatField()),
                0)
        ).order_by()

        return {
            stats['week']: stats
            for stats in queryset
        }

    def _get_payrolls_stats(self) -> dict:
        queryset = SpentTime.objects.annotate(
            week=TruncWeek('date')
        ).annotate_payrolls().filter(
            user=self.user,
            date__gte=self.start,
            date__lt=self.end,
            week__isnull=False
        ).values(
            'week'
        ).annotate(
            total_payroll=Coalesce(Sum('payroll'), 0),
            total_paid=Coalesce(Sum('paid'), 0)
        ).order_by()

        return {
            stats['week']: stats
            for stats in queryset
        }
