from typing import ClassVar, Optional, Iterable

from django.db.models import Sum
from django.db.models.functions import Coalesce

from apps.core.consts import SECONDS_PER_HOUR
from apps.development.models.issue import STATE_OPENED
from apps.payroll.models import SpentTime
from apps.users.models import User

PROBLEM_PAYROLL_OPENED_OVERFLOW = 'payroll_opened_overflow'


class BaseProblemChecker:
    problem_code: ClassVar[Optional[str]] = None

    def check(self, user: User) -> Optional[str]:
        if self.has_problem(user):
            return self.problem_code

    def has_problem(self, user: User) -> bool:
        raise NotImplementedError


class PayrollOpenedOverflowChecker(BaseProblemChecker):
    problem_code = PROBLEM_PAYROLL_OPENED_OVERFLOW

    def has_problem(self, user: User) -> bool:
        total_spend = SpentTime.objects.filter(
            salary__isnull=True,
            user=user,
            issues__state=STATE_OPENED
        ).aggregate(
            total_time_spent=Coalesce(Sum('time_spent'), 0)
        )['total_time_spent']

        return total_spend > user.daily_work_hours * SECONDS_PER_HOUR * 1.5


checkers = [
    checker_class()
    for checker_class in BaseProblemChecker.__subclasses__()
]


def get_user_problems(user: User) -> Iterable[str]:
    problems = []

    for checker in checkers:
        problem = checker.check(user)
        if problem:
            problems.append(problem)

    return problems
