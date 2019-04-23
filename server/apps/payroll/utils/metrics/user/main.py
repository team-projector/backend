from django.db.models import Sum

from apps.development.models.issue import Issue, STATE_CLOSED, STATE_OPENED
from apps.payroll.models import Bonus, Penalty, SpentTime
from apps.users.models import User


class UserMetrics:
    payroll_closed: float = 0
    payroll_opened: float = 0
    bonus: float = 0
    penalty: float = 0
    issues_opened_count: int = 0


class UserMetricsCalculator:
    def calculate(self, user: User) -> UserMetrics:
        metrics = UserMetrics()

        metrics.issues_opened_count = self._get_issues_opened_count(user)
        metrics.bonus = self._get_bonus(user)
        metrics.penalty = self._get_penalty(user)
        metrics.payroll_opened = self._get_payroll_opened(user)
        metrics.payroll_closed = self._get_payroll_closed(user)

        return metrics

    @staticmethod
    def _get_issues_opened_count(user: User) -> int:
        return Issue.objects.filter(user=user, state=STATE_OPENED).count()

    @staticmethod
    def _get_bonus(user: User) -> float:
        return (Bonus.objects
                .filter(user=user, salary__isnull=True)
                .aggregate(total_bonus=Sum('sum'))['total_bonus'] or 0)

    @staticmethod
    def _get_penalty(user: User) -> float:
        return (Penalty.objects
                .filter(user=user, salary__isnull=True)
                .aggregate(total_penalty=Sum('sum'))['total_penalty'] or 0)

    @staticmethod
    def _get_payroll_opened(user: User) -> float:
        return (SpentTime.objects
                .filter(salary__isnull=True, user=user, issues__state=STATE_OPENED)
                .aggregate(total_sum=Sum('sum'))['total_sum'] or 0)

    @staticmethod
    def _get_payroll_closed(user: User) -> float:
        return (SpentTime.objects
                .filter(salary__isnull=True, user=user, issues__state=STATE_CLOSED)
                .aggregate(total_sum=Sum('sum'))['total_sum'] or 0)
