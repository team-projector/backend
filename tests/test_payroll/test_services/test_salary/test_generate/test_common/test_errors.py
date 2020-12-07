from datetime import timedelta

import pytest

from apps.development.models.issue import IssueState
from apps.payroll.models import Salary
from apps.payroll.services.salary.errors import EmptySalaryError
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory


def test_no_payrolls(user, calculator):
    """
    Test no payrolls.

    :param user:
    :param calculator:
    """
    salary = None

    with pytest.raises(EmptySalaryError):
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

    with pytest.raises(EmptySalaryError):
        salary = calculator.generate(user)

    assert salary is None
    assert not Salary.objects.exists()
