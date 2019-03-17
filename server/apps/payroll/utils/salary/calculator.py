from datetime import date

from django.db import transaction
from django.db.models import Sum

from apps.payroll.models import User, Salary, Payroll, SpentTime, Penalty, Bonus


class SalaryCalculator:
    def __init__(self, initiator: User, period_from: date, period_to: date):
        self.initiator = initiator
        self.period_from = period_from
        self.period_to = period_to

    @transaction.atomic
    def generate(self, user: User) -> Salary:
        salary = Salary.objects.create(
            created_by=self.initiator,
            user=user,
            period_from=self.period_from,
            period_to=self.period_to
        )

        Payroll.objects.filter(salary__isnull=True, user=user).update(salary=salary)

        spent_data = SpentTime.objects \
            .filter(salary=salary) \
            .aggregate(total_sum=Sum('sum'),
                       total_time_spent=Sum('time_spent'))

        salary.sum = spent_data['total_sum'] or 0
        salary.charged_time = spent_data['total_time_spent'] or 0

        salary.penalty = (Penalty.objects
                          .filter(salary=salary)
                          .aggregate(total_sum=Sum('sum'))['total_sum'] or 0)

        salary.bonus = (Bonus.objects
                        .filter(salary=salary)
                        .aggregate(total_sum=Sum('sum'))['total_sum'] or 0)

        salary.total = salary.sum + salary.bonus - salary.penalty
        salary.save()

        return salary
