# -*- coding: utf-8 -*-

from datetime import date
from typing import Iterable, List

from apps.development.models import Team
from apps.payroll.services.metrics.progress.user import (
    User,
    UserProgressMetrics,
)


class TeamMemberProgressMetrics:
    """Team member progress metrics."""

    user: User
    metrics: Iterable[UserProgressMetrics] = []


class ProgressMetricsProvider:
    """Progress metrics provider."""

    def __init__(
        self,
        team: Team,
        start: date,
        end: date,
    ):
        self.team = team
        self.start = start
        self.end = end

    def get_metrics(self) -> Iterable[TeamMemberProgressMetrics]:
        """Calculate and return metrics."""
        metrics: List[TeamMemberProgressMetrics] = []
        for member in self.team.members.all():
            user_metrics = TeamMemberProgressMetrics()

            user_metrics.user = member
            user_metrics.metrics = self.get_user_metrics(member)

            metrics.append(user_metrics)

        return metrics

    def get_user_metrics(self, user: User) -> Iterable[UserProgressMetrics]:
        """Method should be implemented in subclass."""
        raise NotImplementedError
