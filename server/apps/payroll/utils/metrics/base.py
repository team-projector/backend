from datetime import date
from typing import Iterable

from django.db.models import F, Sum

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


class MetricsCalculator:
    def __init__(self, user: User, start: date, end: date):
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

    def get_active_issues(self):
        return list(Issue.objects.annotate(remaining=F('time_estimate') - F('total_time_spent'))
                    .filter(employee=self.user, remaining__gt=0)
                    .exclude(state='closed')
                    .values('id', 'due_date', 'remaining'))
