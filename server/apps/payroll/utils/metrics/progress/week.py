from datetime import date, timedelta
from typing import Iterable, List

from django.db.models import Avg, Case, Count, F, FloatField, Q, QuerySet, Sum, When
from django.db.models.functions import Cast, TruncWeek
from django.utils.timezone import make_aware

from apps.core.utils.date import begin_of_week, date2datetime
from apps.development.models import Issue, STATE_CLOSED, STATE_OPENED
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

            self._adjust_deadlines(metric)
            self._adjust_efficiency(metric)
            self._adjust_payrolls(metric)

            if week in spents:
                spent = spents[week]
                metric.time_spent = spent['period_spent']

        return metrics

    def modify_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.annotate(week=TruncWeek('date')).values('week')

    def _adjust_deadlines(self, metric: UserProgressMetrics) -> None:
        issues_stats = Issue.objects.filter(user=self.user, due_date__range=(metric.start, metric.end)) \
            .exclude(state=STATE_CLOSED) \
            .aggregate(issues_count=Count('*'),
                       total_time_estimate=Sum('time_estimate'))

        metric.issues_count = issues_stats['issues_count']
        metric.time_estimate = issues_stats['total_time_estimate'] or 0

    def _adjust_efficiency(self, metric: UserProgressMetrics) -> None:
        issues_stats = Issue.objects.filter(user=self.user,
                                            closed_at__range=(
                                                make_aware(date2datetime(metric.start)),
                                                make_aware(date2datetime(metric.end))
                                            ),
                                            state=STATE_CLOSED,
                                            total_time_spent__gt=0,
                                            time_estimate__gt=0) \
            .annotate(efficiency=Cast(F('time_estimate'), FloatField()) / Cast(F('total_time_spent'), FloatField())) \
            .aggregate(avg_efficiency=Avg('efficiency'))

        metric.efficiency = issues_stats['avg_efficiency'] or 0

    def _adjust_payrolls(self, metric: UserProgressMetrics) -> None:
        data = SpentTime.objects \
            .filter(user=self.user,
                    date__gte=metric.start,
                    date__lt=metric.end) \
            .annotate(payroll_opened=Case(When(Q(salary__isnull=True) & Q(issues__state=STATE_OPENED), then=F('sum')),
                                          default=0,
                                          output_field=FloatField()),
                      payroll_closed=Case(When(Q(salary__isnull=True) & Q(issues__state=STATE_CLOSED), then=F('sum')),
                                          default=0,
                                          output_field=FloatField()),
                      paid=Case(When(salary__isnull=False, then=F('sum')),
                                default=0,
                                output_field=FloatField())) \
            .aggregate(total_payroll_opened=Sum('payroll_opened'),
                       total_payroll_closed=Sum('payroll_closed'),
                       total_paid=Sum('paid'))

        metric.payroll_opened = data['total_payroll_opened'] or 0
        metric.payroll_closed = data['total_payroll_closed'] or 0
        metric.paid = data['total_paid'] or 0

    def _get_weeks(self) -> List[date]:
        ret: List[date] = []
        current = self.start

        while current <= self.end:
            ret.append(begin_of_week(current))
            current += WEEK_STEP

        return ret
