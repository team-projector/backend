# -*- coding: utf-8 -*-

from datetime import date
from typing import Any, Dict, Iterable, List, Optional

from django.db.models import F
from django.utils.functional import cached_property

from apps.core.utils.time import seconds
from apps.development.models.issue import ISSUE_STATES, Issue
from apps.users.models import User


class UserProgressMetrics:
    start: Optional[date] = None
    end: Optional[date] = None
    time_spent: int = 0
    time_estimate: int = 0
    time_remains: int = 0
    loading: int = 0
    efficiency: float = 0
    issues_count: int = 0
    payroll: float = 0
    paid: float = 0
    planned_work_hours: int = 0


class ProgressMetricsProvider:
    def __init__(
        self,
        user: User,
        start: date,
        end: date,
    ):
        self.user = user
        self.start = start
        self.end = end

    @cached_property
    def max_day_loading(self):
        return seconds(hours=self.user.daily_work_hours)

    def get_metrics(self) -> Iterable[UserProgressMetrics]:
        raise NotImplementedError

    def get_active_issues(self) -> List[Dict[str, Any]]:
        return list(
            Issue.objects.annotate(
                remaining=F('time_estimate') - F('total_time_spent'),
            ).filter(
                user=self.user,
                remaining__gt=0,
            ).exclude(
                state=ISSUE_STATES.closed,
            ).values('id', 'due_date', 'remaining'),
        )
