from datetime import date, datetime, timedelta
from typing import Iterable, List

from django.conf import settings
from django.db.models import Count, F, Sum
from django.db.models.functions import TruncDay
from django.utils import timezone

from apps.development.models import Issue
from apps.payroll.models import SpentTime
from apps.users.models import User


class Metric:
    start = None
    end = None
    time_spent = 0
    time_estimate = 0
    loading = 0
    efficiency = 0
    earnings = 0
    issues = 0


class BaseMetricsCalculator:
    def __init__(self, user: User, start: datetime, end: datetime):
        self.user = user
        self.start = start
        self.end = end

    def calculate(self) -> Iterable[Metric]:
        raise NotImplementedError

    def get_spents(self):
        queryset = SpentTime.objects.filter(employee=self.user,
                                            date__range=(self.start, self.end))
        queryset = self.modify_queryset(queryset)

        return queryset.annotate(period_spent=Sum('time_spent')).order_by()

    def modify_queryset(self, queryset):
        raise NotImplementedError


DAY_STEP = timedelta(days=1)
MAX_DAY_LOADING = timedelta(hours=8).total_seconds()


class DayMetricsCalculator(BaseMetricsCalculator):
    def calculate(self) -> Iterable[Metric]:
        metrics = []

        spents = {
            spent['day']: spent
            for spent in self.get_spents()
        }

        current = self.start
        now = timezone.now().date()

        active_issues = list(Issue.objects.annotate(remaining=F('time_estimate') - F('total_time_spent'))
                             .filter(employee=self.user, remaining__gt=0)
                             .exclude(state='closed')
                             .values('id', 'due_date', 'remaining')) \
            if now > self.start \
            else []

        while current <= self.end:
            metric = Metric()
            metrics.append(metric)

            metric.start = metric.end = current
            deadline_stats = Issue.objects.filter(employee=self.user, due_date=current) \
                .exclude(state='closed') \
                .aggregate(issues_count=Count('*'),
                           total_time_estimate=Sum('time_estimate'))

            metric.issues = deadline_stats['issues_count']
            metric.time_estimate = deadline_stats['total_time_estimate'] or 0

            if current in spents:
                spent = spents[current]
                metric.time_spent = spent['period_spent']

            if self._is_apply_loading(current, now):
                self._update_loading(metric, active_issues)

            current += DAY_STEP

        return metrics

    @staticmethod
    def _is_apply_loading(day: date, now: date) -> bool:
        return day >= now and day.weekday() not in settings.TP_WEEKENDS_DAYS

    @staticmethod
    def _update_loading(metric: Metric, active_issues: List[dict]) -> None:
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

    def modify_queryset(self, queryset):
        return queryset.annotate(day=TruncDay('date')).values('day')


def create_calculator(user: User, start: datetime, end: datetime, group: str):
    if group == 'day':
        return DayMetricsCalculator(user, start, end)
