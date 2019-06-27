from datetime import date
from typing import Iterable, List

from apps.development.models import Team
from apps.payroll.services.metrics.progress.user import (
    User, UserProgressMetrics
)


class TeamMemberProgressMetrics:
    user: int
    metrics: Iterable[UserProgressMetrics] = []


class ProgressMetricsCalculator:
    def __init__(self,
                 team: Team,
                 start: date,
                 end: date):
        self.team = team
        self.start = start
        self.end = end

    def calculate(self) -> Iterable[TeamMemberProgressMetrics]:
        metrics: List[TeamMemberProgressMetrics] = []
        for member in self.team.members.all():
            user_metrics = TeamMemberProgressMetrics()

            user_metrics.user = member.id
            user_metrics.metrics = self.calculate_user_metrics(member)

            metrics.append(user_metrics)

        return metrics

    def calculate_user_metrics(self,
                               user: User) -> Iterable[UserProgressMetrics]:
        raise NotImplementedError
