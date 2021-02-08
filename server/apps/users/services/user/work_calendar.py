from dataclasses import dataclass
from datetime import date
from typing import List

from django.db import models

from apps.development.models import Issue
from apps.users.services.user.metrics import get_progress_metrics
from apps.users.services.user.metrics.progress.main import GroupProgressMetrics
from apps.users.services.user.metrics.progress.provider import (
    UserProgressMetrics,
)


@dataclass
class WorkCalendar:
    """Work calendar data."""

    date: date
    metrics: UserProgressMetrics
    issues: models.QuerySet


def get_work_calendar(user, start_date, end_date) -> List[WorkCalendar]:
    """Get work calendar."""
    user_metrics = get_progress_metrics(
        user,
        start_date,
        end_date,
        GroupProgressMetrics.DAY,
    )

    return [
        WorkCalendar(
            date=metrics.start,
            metrics=metrics,
            issues=Issue.objects.filter(user=user, due_date=metrics.start),
        )
        for metrics in user_metrics
    ]
