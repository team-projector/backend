from datetime import timedelta
from decimal import Decimal

import pytest
from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.payroll.models import Payroll, Salary
from apps.payroll.services.salary.exceptions import EmptySalaryException
from tests.test_development.factories import IssueFactory, MergeRequestFactory
from tests.test_payroll.factories import (
    BonusFactory,
    IssueSpentTimeFactory,
    MergeRequestSpentTimeFactory,
    PenaltyFactory,
    SalaryFactory,
)
from tests.test_payroll.test_services.test_salary.test_generate import checkers
from tests.test_users.factories.user import UserFactory


def test_common(user, calculator):
    """
    Test common.

    :param user:
    :param calculator:
    """
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
    MergeRequestSpentTimeFactory.create(
        user=user,
        base=MergeRequestFactory.create(state=IssueState.CLOSED),
        time_spent=timedelta(hours=5).total_seconds(),
    )

    salary = calculator.generate(user)
    checkers.check_salary(
        salary,
        charged_time=seconds(hours=9),
        sum=user.hour_rate * 9,
        taxes=salary.total * salary.tax_rate,
        hour_rate=100,
        tax_rate=15,
        position=user.position,
        total=salary.sum,
    )

    assert Payroll.objects.filter(salary=salary).count() == 4


def test_no_payrolls(user, calculator):
    """
    Test no payrolls.

    :param user:
    :param calculator:
    """
    salary = None

    with pytest.raises(EmptySalaryException):
        salary = calculator.generate(user)

    assert salary is None
    assert Salary.objects.count() == 0


def test_empty_total(user, calculator):
    """
    Test empty total.

    :param user:
    :param calculator:
    """
    salary = None

    issue = IssueFactory.create(state=IssueState.CLOSED)
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=timedelta(hours=1).total_seconds(),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=-timedelta(hours=1).total_seconds(),
    )

    with pytest.raises(EmptySalaryException):
        salary = calculator.generate(user)

    assert salary is None
    assert not Salary.objects.exists()


def test_with_penalty(user, calculator):
    """
    Test with penalty.

    :param user:
    :param calculator:
    """
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

    penalty = PenaltyFactory.create(user=user, sum=100)

    salary = calculator.generate(user)

    checkers.check_salary(
        salary,
        charged_time=seconds(hours=4),
        hour_rate=100,
        tax_rate=user.tax_rate,
        sum=user.hour_rate * 4,
        penalty=penalty.sum,
        taxes=salary.total * salary.tax_rate,
        total=salary.sum - penalty.sum,
        position=user.position,
    )

    assert Payroll.objects.filter(salary=salary).count() == 4


def test_with_bonus(user, calculator):
    """
    Test with bonus.

    :param user:
    :param calculator:
    """
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

    salary = calculator.generate(user)

    checkers.check_salary(
        salary,
        charged_time=seconds(hours=4),
        hour_rate=100,
        tax_rate=user.tax_rate,
        sum=user.hour_rate * 4,
        bonus=bonus.sum,
        taxes=salary.total * salary.tax_rate,
        total=salary.sum + bonus.sum,
        position=user.position,
    )

    assert Payroll.objects.filter(salary=salary).count() == 4


def test_penalty_and_bonus(user, calculator):
    """
    Test penalty and bonus.

    :param user:
    :param calculator:
    """
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
        tax_rate=user.tax_rate,
        sum=user.hour_rate * 4,
        bonus=bonus.sum,
        penalty=penalty.sum,
        taxes=salary.total * salary.tax_rate,
        total=salary.sum + bonus.sum - penalty.sum,
        position=user.position,
    )

    assert Payroll.objects.filter(salary=salary).count() == 5


def test_some_already_with_salary(user, calculator):
    """
    Test some already with salary.

    :param user:
    :param calculator:
    """
    prev_salary = SalaryFactory.create(user=user)
    issue = IssueFactory.create(state=IssueState.CLOSED)

    IssueSpentTimeFactory.create(
        salary=prev_salary,
        base=issue,
        user=user,
        time_spent=timedelta(hours=1).total_seconds(),
    )
    IssueSpentTimeFactory.create(
        salary=prev_salary,
        base=issue,
        user=user,
        time_spent=-timedelta(hours=2).total_seconds(),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=timedelta(hours=5).total_seconds(),
    )

    bonus = BonusFactory.create(user=user)
    PenaltyFactory.create(user=user, salary=prev_salary, sum=100)

    salary = calculator.generate(user)

    checkers.check_salary(
        salary,
        charged_time=seconds(hours=5),
        hour_rate=100,
        tax_rate=user.tax_rate,
        sum=user.hour_rate * 5,
        bonus=bonus.sum,
        taxes=salary.total * salary.tax_rate,
        total=salary.sum + bonus.sum,
        position=user.position,
    )

    assert Payroll.objects.filter(salary=salary).count() == 2
    assert Payroll.objects.filter(salary=prev_salary).count() == 3


def test_with_another_user(user, calculator):
    """
    Test with another user.

    :param user:
    :param calculator:
    """
    user2 = UserFactory.create()
    issue = IssueFactory.create(state=IssueState.CLOSED)

    IssueSpentTimeFactory.create(
        user=user2,
        base=issue,
        time_spent=timedelta(hours=1).total_seconds(),
    )
    IssueSpentTimeFactory.create(
        user=user2,
        base=issue,
        time_spent=-timedelta(hours=2).total_seconds(),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=timedelta(hours=5).total_seconds(),
    )

    BonusFactory.create(user=user2)
    penalty = PenaltyFactory.create(user=user, sum=100)

    salary = calculator.generate(user)

    checkers.check_salary(
        salary,
        charged_time=seconds(hours=5),
        hour_rate=100,
        tax_rate=user.tax_rate,
        sum=user.hour_rate * 5,
        penalty=penalty.sum,
        taxes=salary.total * salary.tax_rate,
        total=salary.sum - penalty.sum,
        position=user.position,
    )

    assert Payroll.objects.filter(salary=salary).count() == 2


def test_with_opened_issues_mr(user, calculator):
    """
    Test with opened issues mr.

    :param user:
    :param calculator:
    """
    closed_issue = IssueFactory.create(state=IssueState.CLOSED)
    opened_issue = IssueFactory.create(state=IssueState.OPENED)
    opened_mr = MergeRequestFactory.create(state=IssueState.OPENED)

    IssueSpentTimeFactory.create(
        user=user,
        base=opened_issue,
        time_spent=timedelta(hours=1).total_seconds(),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=closed_issue,
        time_spent=-timedelta(hours=2).total_seconds(),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=closed_issue,
        time_spent=timedelta(hours=5).total_seconds(),
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=opened_mr,
        time_spent=timedelta(hours=5).total_seconds(),
    )

    salary = calculator.generate(user)

    checkers.check_salary(
        salary,
        charged_time=seconds(hours=3),
        hour_rate=100,
        tax_rate=user.tax_rate,
        sum=user.hour_rate * 3,
        taxes=salary.total * salary.tax_rate,
        total=salary.sum,
        position=user.position,
    )
    assert Payroll.objects.filter(salary=salary).count() == 2


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
