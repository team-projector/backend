from datetime import datetime, timedelta
from typing import Dict, List

from django.db import models

from apps.development.models import Issue
from apps.development.models.issue import IssueState
from apps.users.logic.services.user.progress import provider
from apps.users.logic.services.user.progress.day.metrics import (
    UserDaysMetricsGenerator,
)

DAY_STEP = timedelta(days=1)


class DayMetricsProvider(provider.ProgressMetricsProvider):
    """Day metrics provider."""

    def get_metrics(self) -> provider.UserProgressMetricsList:
        """Calculate and return metrics."""
        now = datetime.now().date()

        active_issues = self._get_active_issues() if now <= self.end else []

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

    def _get_metrics(  # noqa: WPS211
        self,
        generator: UserDaysMetricsGenerator,
    ) -> provider.UserProgressMetricsList:
        """
        Get metrics.

        :param generator:
        :type generator: UserDaysMetricsGenerator
        :rtype: provider.UserProgressMetricsList
        """
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
        active_issues: List[Dict[str, object]],
        generator: UserDaysMetricsGenerator,
    ) -> None:
        """
        Replay loading.

        :param now:
        :param active_issues:
        :type active_issues: List[Dict]
        :param generator:
        :type generator: UserDaysMetricsGenerator
        :rtype: None
        """
        current = now

        while current < self.start:
            if not active_issues:
                return

            generator.replay_loading(current)

            current += DAY_STEP

    def _get_active_issues(self) -> List[Dict[str, object]]:
        """Get open issues with time remains."""
        return list(
            Issue.objects.annotate(
                remaining=(
                    models.F("time_estimate") - models.F("total_time_spent")
                ),
            )
            .filter(user=self.user, remaining__gt=0)
            .exclude(state=IssueState.CLOSED)
            .values("id", "due_date", "remaining"),
        )
