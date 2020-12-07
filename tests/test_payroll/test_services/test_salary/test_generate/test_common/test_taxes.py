from datetime import timedelta
from decimal import Decimal

from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.payroll.models import Payroll
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import (
    BonusFactory,
    IssueSpentTimeFactory,
    PenaltyFactory,
)
from tests.test_payroll.test_services.test_salary.test_generate import checkers


def test_taxes(user, calculator):
    """
    Test taxes.

    :param user:
    :param calculator:
    """
    user.tax_rate = 0.3
    user.save()

    issue = IssueFactory.create(state=IssueState.CLOSED)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=timedelta(hours=1).total_seconds(),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=-timedelta(hours=2).total_seconds(),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=timedelta(hours=5).total_seconds(),
    )

    bonus = BonusFactory.create(user=user)
    penalty = PenaltyFactory.create(user=user, sum=100)

    salary = calculator.generate(user)

    checkers.check_salary(
        salary,
        charged_time=seconds(hours=4),
        hour_rate=100,
        bonus=bonus.sum,
        penalty=penalty.sum,
        sum=user.hour_rate * 4,
        tax_rate=user.tax_rate,
        taxes=salary.total * Decimal.from_float(user.tax_rate),
        total=salary.sum + bonus.sum - penalty.sum,
        position=user.position,
    )
    assert Payroll.objects.filter(salary=salary).count() == 5
