from datetime import date
from typing import Any, Dict, Iterable, List, Optional

from django.db.models import F, QuerySet, Sum

from apps.development.models import Issue, STATE_CLOSED
from apps.payroll.models import SpentTime
from apps.users.models import User


class Metric:
    start: Optional[date] = None
    end: Optional[date] = None
    time_spent: int = 0
    time_estimate: int = 0
    time_remains: int = 0
    loading: int = 0
    efficiency: float = 0
    earnings: float = 0
    issues: int = 0


class MetricsCalculator:
    def __init__(self, user: User, start: date, end: date):
        self.user = user
        self.start = start
        self.end = end

    def calculate(self) -> Iterable[Metric]:
        raise NotImplementedError

    def get_spents(self) -> QuerySet:
        queryset = SpentTime.objects.filter(employee=self.user,
                                            date__range=(self.start, self.end))
        queryset = self.modify_queryset(queryset)

        return queryset.annotate(period_spent=Sum('time_spent')).order_by()

    def modify_queryset(self, queryset: QuerySet):
        raise NotImplementedError

    def get_active_issues(self) -> List[Dict[str, Any]]:
        return list(Issue.objects.annotate(remaining=F('time_estimate') - F('total_time_spent'))
                    .filter(employee=self.user, remaining__gt=0)
                    .exclude(state=STATE_CLOSED)
                    .values('id', 'due_date', 'remaining'))
