from datetime import date, timedelta
from typing import Iterable, List

from django.conf import settings
from django.db.models import Case, Count, F, IntegerField, Q, QuerySet, Sum, Value, When
from django.db.models.functions import Coalesce, TruncDay
from django.utils import timezone

from apps.development.models.issue import Issue, STATE_CLOSED
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

        due_day_stats = self._get_due_day_stats()

        while current <= self.end:
            metric = UserProgressMetrics()
            metrics.append(metric)

            metric.start = metric.end = current
            metric.planned_work_hours = self.user.daily_work_hours

            if current in due_day_stats:
                current_stats = due_day_stats[current]
                metric.issues_count = current_stats['issues_count']
                metric.time_estimate = current_stats['total_time_estimate']
                metric.time_remains = current_stats['total_time_remains']

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
        data = SpentTime.objects.filter(
            user=self.user,
            date=metric.start
        ).aggregate_payrolls()

        metric.payroll = data['total_payroll']
        metric.paid = data['total_paid']

    def modify_queryset(self, queryset: QuerySet) -> QuerySet:
        return queryset.annotate(day=TruncDay('date')).values('day')

    def _get_due_day_stats(self) -> dict:
        queryset = Issue.objects.annotate(
            due_date_truncated=TruncDay('due_date'),
            time_remains=Case(
                When(
                    Q(time_estimate__gt=F('total_time_spent')) & ~Q(state=STATE_CLOSED),
                    then=F('time_estimate') - F('total_time_spent')),
                default=Value(0),
                output_field=IntegerField()
            ),
        ).filter(
            user=self.user,
            due_date_truncated__isnull=False
        ).values(
            'due_date_truncated'
        ).annotate(
            issues_count=Count('*'),
            total_time_estimate=Coalesce(Sum('time_estimate'), 0),
            total_time_remains=Coalesce(Sum('time_remains'), 0)
        ).order_by()

        return {
            stats['due_date_truncated']: stats
            for stats in queryset
        }
