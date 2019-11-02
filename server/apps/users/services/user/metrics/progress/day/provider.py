# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from typing import Any, Dict, List

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

        active_issues = self.get_active_issues() if now <= self.end else []

        metrics_generator = UserDaysMetricsGenerator(
            self.user,
            self.start,
            self.end,
            now,
            self.max_day_loading,
            active_issues,
        )

        if self.start > now:
            self._replay_loading(
                now,
                active_issues,
                metrics_generator,
            )

        return self._get_metrics(metrics_generator)

    def _get_metrics(  # noqa WPS211
        self,
        metrics_generator: UserDaysMetricsGenerator,
    ) -> provider.UserProgressMetricsList:
        current = self.start

        metrics: provider.UserProgressMetricsList = []

        while current <= self.end:
            metric = metrics_generator.generate(current)
            metrics.append(metric)

            current += DAY_STEP

        return metrics

    def _replay_loading(
        self,
        now,
        active_issues: List[Dict[str, Any]],
        metrics_generator: UserDaysMetricsGenerator,
    ) -> None:
        current = now

        while current < self.start:
            if not active_issues:
                return

            metrics_generator.replay_loading(current)

            current += DAY_STEP
