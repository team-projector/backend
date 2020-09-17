# -*- coding: utf-8 -*-

from datetime import date
from typing import List

from apps.development.models import Team
from apps.users.models import User
from apps.users.services.user.metrics import UserProgressMetricsList


class TeamMemberProgressMetrics:
    """Team member progress metrics."""

    user: User
    metrics: UserProgressMetricsList = []


class ProgressMetricsProvider:
    """Progress metrics provider."""

    def __init__(
        self,
        team: Team,
        start: date,
        end: date,
    ):
        """Initialize self."""
        self.team = team
        self.start = start
        self.end = end

    def get_metrics(self) -> List[TeamMemberProgressMetrics]:
        """Calculate and return metrics."""
        metrics: List[TeamMemberProgressMetrics] = []
        for member in self.team.members.all():
            user_metrics = TeamMemberProgressMetrics()

            user_metrics.user = member
            user_metrics.metrics = self.get_user_metrics(member)

            metrics.append(user_metrics)

        return metrics

    def get_user_metrics(self, user: User) -> UserProgressMetricsList:
        """Method should be implemented in subclass."""
        raise NotImplementedError
