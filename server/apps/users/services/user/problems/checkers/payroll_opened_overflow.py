# -*- coding: utf-8 -*-

from django.db.models import Sum
from django.db.models.functions import Coalesce

from apps.core.consts import SECONDS_PER_HOUR
from apps.development.models.issue import ISSUE_STATES
from apps.payroll.models import SpentTime
from apps.users.models import User
from apps.users.services.user.problems.checkers.base import BaseProblemChecker

PROBLEM_PAYROLL_OPENED_OVERFLOW = 'payroll_opened_overflow'
PROBLEM_PAYROLL_OVERFLOW_RATIO = 1.5


class PayrollOpenedOverflowChecker(BaseProblemChecker):
    """A class indicates on problem with payroll overflow."""

    problem_code = PROBLEM_PAYROLL_OPENED_OVERFLOW

    def has_problem(self, user: User) -> bool:
        """Has problem if time spent more than daily work hours of user."""
        total_spend = SpentTime.objects.filter(
            salary__isnull=True,
            user=user,
            issues__state=ISSUE_STATES.opened,
        ).aggregate(
            total_time_spent=Coalesce(Sum('time_spent'), 0),
        )['total_time_spent']

        return total_spend > user.daily_work_hours * (
            SECONDS_PER_HOUR * PROBLEM_PAYROLL_OVERFLOW_RATIO
        )