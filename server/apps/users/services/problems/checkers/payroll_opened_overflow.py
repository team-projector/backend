# -*- coding: utf-8 -*-

from django.db.models import Sum
from django.db.models.functions import Coalesce

from apps.core.consts import SECONDS_PER_HOUR
from apps.development.models.issue import ISSUE_STATES
from apps.payroll.models import SpentTime
from apps.users.models import User
from .base import BaseProblemChecker

PROBLEM_PAYROLL_OPENED_OVERFLOW = 'payroll_opened_overflow'


class PayrollOpenedOverflowChecker(BaseProblemChecker):
    problem_code = PROBLEM_PAYROLL_OPENED_OVERFLOW

    def has_problem(self, user: User) -> bool:
        total_spend = SpentTime.objects.filter(
            salary__isnull=True,
            user=user,
            issues__state=ISSUE_STATES.opened,
        ).aggregate(
            total_time_spent=Coalesce(Sum('time_spent'), 0),
        )['total_time_spent']

        return total_spend > user.daily_work_hours * SECONDS_PER_HOUR * 1.5
