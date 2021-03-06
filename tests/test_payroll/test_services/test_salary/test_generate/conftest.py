from datetime import timedelta

import pytest
from django.utils import timezone

from apps.payroll.services.salary.calculator import SalaryCalculator
from tests.test_skills.factories import PositionFactory
from tests.test_users.factories.user import UserFactory


@pytest.fixture()
def user(db):
    """
    User.

    :param db:
    """
    return UserFactory.create(
        hour_rate=100,
        tax_rate=15,
        position=PositionFactory.create(),
    )


@pytest.fixture()
def calculator(db):
    """
    Calculator.

    :param db:
    """
    return SalaryCalculator(
        UserFactory.create(login="initiator"),
        period_from=timezone.now() - timedelta(days=30),
        period_to=timezone.now(),
    )
