from contextlib import suppress
from datetime import date
from decimal import Decimal
from typing import Optional

from django.db import models, transaction

from apps.development.models.issue import IssueState
from apps.development.models.merge_request import MergeRequestState
from apps.payroll.models import Bonus, Penalty, Salary, SpentTime
from apps.payroll.services.salary.exceptions import EmptySalaryError
from apps.users.models import User


class SalaryCalculator:
    """Salary calculator."""

    def __init__(
        self,
        initiator: User,
        period_from: date,
        period_to: date,
    ):
        """Initialize self."""
        self.initiator = initiator
        self.period_from = period_from
        self.period_to = period_to

    def generate_bulk(self):
        """Generate salaries for active users."""
        for user in User.objects.filter(is_active=True):
            with suppress(EmptySalaryError):
                self.generate(user)

    @transaction.atomic
    def generate(self, user: User) -> Optional[Salary]:
        """Generate salary for user."""
        salary = Salary.objects.create(
            created_by=self.initiator,
            user=user,
            hour_rate=user.hour_rate,
            tax_rate=user.tax_rate,
            position=user.position,
            period_from=self.period_from,
            period_to=self.period_to,
        )

        self._lock_payrolls(user, salary)

        spent_data = self._get_spent_data(salary)

        salary.sum = spent_data["total_sum"] or 0  # noqa: WPS125
        salary.charged_time = spent_data["total_time_spent"] or 0
        salary.penalty = self._get_penalty(salary)
        salary.bonus = self._get_bonus(salary)
        salary.total = salary.sum + salary.bonus - salary.penalty

        if not salary.total:
            raise EmptySalaryError

        if user.tax_rate:
            salary.taxes = salary.total * Decimal.from_float(user.tax_rate)

        salary.save()
        return salary

    def _get_spent_data(self, salary: Salary) -> models.QuerySet:
        """
        Get spent data.

        :param salary:
        :type salary: Salary
        :rtype: models.QuerySet
        """
        return SpentTime.objects.filter(salary=salary).aggregate(
            total_sum=models.Sum("sum"),
            total_time_spent=models.Sum("time_spent"),
        )

    def _get_penalty(self, salary: Salary) -> models.QuerySet:
        """
        Get penalty.

        :param salary:
        :type salary: Salary
        :rtype: models.QuerySet
        """
        return (
            Penalty.objects.filter(salary=salary).aggregate(
                total_sum=models.Sum("sum"),
            )["total_sum"]
            or 0
        )

    def _get_bonus(self, salary: Salary) -> models.QuerySet:
        """
        Get bonus.

        :param salary:
        :type salary: Salary
        :rtype: models.QuerySet
        """
        return (
            Bonus.objects.filter(salary=salary).aggregate(
                total_sum=models.Sum("sum"),
            )["total_sum"]
            or 0
        )

    def _lock_payrolls(self, user: User, salary: Salary) -> int:
        """
        Lock payrolls.

        :param user:
        :type user: User
        :param salary:
        :type salary: Salary
        :rtype: int
        """
        locked = Penalty.objects.filter(
            salary__isnull=True,
            user=user,
        ).update(salary=salary)
        locked += Bonus.objects.filter(salary__isnull=True, user=user).update(
            salary=salary,
        )

        locked += (
            SpentTime.objects.filter(salary__isnull=True, user=user)
            .filter(
                models.Q(issues__state=IssueState.CLOSED)
                | models.Q(
                    mergerequests__state__in=(
                        MergeRequestState.CLOSED,
                        MergeRequestState.MERGED,
                    ),
                ),
            )
            .update(salary=salary)
        )

        if locked == 0:
            raise EmptySalaryError

        return locked
