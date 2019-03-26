from datetime import date, timedelta
from typing import Iterable, List

from django.conf import settings
from django.db.models import Case, Count, F, IntegerField, Q, QuerySet, Sum, Value, When
from django.db.models.functions import TruncDay
from django.utils import timezone

from apps.development.models import Issue, STATE_CLOSED
from apps.payroll.models import SpentTime
from .base import ProgressMetricsCalculator, UserProgressMetrics

DAY_STEP = timedelta(days=1)
MAX_DAY_LOADING = timedelta(hours=8).total_seconds()


class DayMetricsCalculator(ProgressMetricsCalculator):
    def calculate(self) -> Iterable[UserProgressMetrics]:
        metrics = []

        spents = {
            spent['day']: spent
            for spent in self.get_spents()
        }

        current = self.start
        now = timezone.now().date()

        active_issues = self.get_active_issues() if now > self.start else []

        while current <= self.end:
            metric = UserProgressMetrics()
            metrics.append(metric)

            metric.start = metric.end = current
            deadline_stats = Issue.objects \
                .annotate(time_remains=Case(When(Q(time_estimate__gt=F('total_time_spent')) & ~Q(state=STATE_CLOSED),
                                                 then=F('time_estimate') - F('total_time_spent')),
                                            default=Value(0),
                                            output_field=IntegerField())) \
                .filter(user=self.user, due_date=current) \
                .aggregate(issues_count=Count('*'),
                           total_time_estimate=Sum('time_estimate'),
                           total_time_remains=Sum('time_remains'))

            metric.issues_count = deadline_stats['issues_count']
            metric.time_estimate = deadline_stats['total_time_estimate'] or 0
            metric.time_remains = deadline_stats['total_time_remains'] or 0

            if current in spents:
                spent = spents[current]
                metric.time_spent = spent['period_spent']

            if self._is_apply_loading(current, now):
                self._update_loading(metric, active_issues)

            self._update_payrolls(metric)

            current += DAY_STEP

        return metrics

    @staticmethod
    def _is_apply_loading(day: date, now: date) -> bool:
        return day >= now and day.weekday() not in settings.TP_WEEKENDS_DAYS

    @staticmethod
    def _update_loading(metric: UserProgressMetrics, active_issues: List[dict]) -> None:
        if not active_issues:
            return

        metric.loading = metric.time_spent

        deadline_issues = [
            issue
            for issue in active_issues
            if issue['due_date'] and issue['due_date'] <= metric.start
        ]

        for issue in deadline_issues:
            metric.loading += issue['remaining']
            active_issues.remove(issue)

        if metric.loading > MAX_DAY_LOADING:
            return

        for issue in active_issues[:]:
            available_time = MAX_DAY_LOADING - metric.loading

            loading = min(available_time, issue['remaining'])

            metric.loading += loading

            issue['remaining'] -= loading
            if not issue['remaining']:
                active_issues.remove(issue)

    def _update_payrolls(self, metric: UserProgressMetrics) -> None:
        data = SpentTime.objects \
            .filter(user=self.user, date=metric.start).aggregate_payrolls()

        metric.payroll = data['total_payroll'] or 0
        metric.paid = data['total_paid'] or 0

    def modify_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.annotate(day=TruncDay('date')).values('day')
