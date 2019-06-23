from contextlib import suppress
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.db.models import Q, Sum

from apps.development.models.issue import STATE_CLOSED
from apps.payroll.models import Bonus, Penalty, Salary, SpentTime
from apps.users.models import User
from .exceptions import EmptySalaryException


class SalaryCalculator:
    def __init__(self, initiator: User, period_from: date, period_to: date):
        self.initiator = initiator
        self.period_from = period_from
        self.period_to = period_to

    def generate_bulk(self):
        for user in User.objects.filter(is_active=True):
            with suppress(EmptySalaryException):
                self.generate(user)

    @transaction.atomic
    def generate(self, user: User) -> Salary:
        salary = Salary.objects.create(
            created_by=self.initiator,
            user=user,
            period_from=self.period_from,
            period_to=self.period_to
        )

        locked = self._lock_payrolls(user, salary)
        if locked == 0:
            raise EmptySalaryException

        spent_data = SpentTime.objects.filter(
            salary=salary
        ).aggregate(
            total_sum=Sum('sum'),
            total_time_spent=Sum('time_spent')
        )

        salary.sum = spent_data['total_sum'] or 0
        salary.charged_time = spent_data['total_time_spent'] or 0

        salary.penalty = Penalty.objects.filter(
            salary=salary
        ).aggregate(
            total_sum=Sum('sum')
        )['total_sum'] or 0

        salary.bonus = Bonus.objects.filter(
            salary=salary
        ).aggregate(
            total_sum=Sum('sum')
        )['total_sum'] or 0

        salary.total = salary.sum + salary.bonus - salary.penalty

        if user.taxes:
            salary.taxes = salary.total * Decimal.from_float(user.taxes)

        salary.save()

        return salary

    @staticmethod
    def _lock_payrolls(user: User, salary: Salary) -> int:
        locked = Penalty.objects.filter(
            salary__isnull=True,
            user=user
        ).update(
            salary=salary
        )
        locked += Bonus.objects.filter(
            salary__isnull=True,
            user=user
        ).update(
            salary=salary
        )
        locked += SpentTime.objects.filter(
            salary__isnull=True,
            user=user
        ).filter(
            Q(issues__state=STATE_CLOSED)
        ).update(
            salary=salary
        )

        return locked
