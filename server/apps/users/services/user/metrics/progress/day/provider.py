# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from typing import Any, Dict, List

from django.db.models import F

from apps.development.models import Issue
from apps.development.models.issue import ISSUE_STATES
from apps.users.services.user.metrics.progress import provider
from apps.users.services.user.metrics.progress.day.metrics import (
    UserDaysMetricsGenerator,
)

DAY_STEP = timedelta(days=1)


class DayMetricsProvider(provider.ProgressMetricsProvider):
    """Day metrics provider."""

    def get_metrics(self) -> provider.UserProgressMetricsList:
        """Calculate and return metrics."""
        now = datetime.now().date()

        active_issues = (
            self._get_active_issues()
            if now <= self.end
            else []
        )

        generator = UserDaysMetricsGenerator(
            self.user,
            self.start,
            self.end,
            active_issues,
        )

        if self.start > now:
            self._replay_loading(
                now,
                active_issues,
                generator,
            )

        return self._get_metrics(generator)

    def _get_metrics(  # noqa WPS211
        self,
        generator: UserDaysMetricsGenerator,
    ) -> provider.UserProgressMetricsList:
        current = self.start

        metrics: provider.UserProgressMetricsList = []

        while current <= self.end:
            metric = generator.generate(current)
            metrics.append(metric)

            current += DAY_STEP

        return metrics

    def _replay_loading(
        self,
        now,
        active_issues: List[Dict[str, Any]],
        generator: UserDaysMetricsGenerator,
    ) -> None:
        current = now

        while current < self.start:
            if not active_issues:
                return

            generator.replay_loading(current)

            current += DAY_STEP

    def _get_active_issues(self) -> List[Dict[str, Any]]:
        """Get open issues with time remains."""
        return list(
            Issue.objects.annotate(
                remaining=F('time_estimate') - F('total_time_spent'),
            ).filter(
                user=self.user,
                remaining__gt=0,
            ).exclude(
                state=ISSUE_STATES.CLOSED,
            ).values('id', 'due_date', 'remaining'),
        )
