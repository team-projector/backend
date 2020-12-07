import pytest

from apps.users.services.user.metrics.main import UserMetricsProvider
from tests.test_payroll.factories import BonusFactory, SalaryFactory
from tests.test_payroll.test_ghl.test_user_metrics.test_provider import (
    checkers,
)
from tests.test_users.factories.user import UserFactory

calculator = UserMetricsProvider


@pytest.fixture()
def user(db):
    """
    User.

    :param db:
    """
    return UserFactory.create(login="user", hour_rate=100, tax_rate=15)


def test_bonus(user):
    """
    Test bonus.

    :param user:
    """
    bonuses = BonusFactory.create_batch(10, user=user)

    metrics = calculator().get_metrics(user)

    bonus = sum(bonus.sum for bonus in bonuses)
    assert metrics["bonus"] == bonus
    checkers.check_taxes(metrics, taxes=bonus * user.tax_rate)


def test_bonus_have_salaries(user):
    """
    Test bonus have salaries.

    :param user:
    """
    bonuses = BonusFactory.create_batch(10, user=user)
    BonusFactory.create_batch(
        5,
        user=user,
        salary=SalaryFactory.create(user=user),
    )

    metrics = calculator().get_metrics(user)

    bonus = sum(bonus.sum for bonus in bonuses)
    assert metrics["bonus"] == bonus
    checkers.check_taxes(metrics, taxes=bonus * user.tax_rate)


def test_bonus_another_user(user):
    """
    Test bonus another user.

    :param user:
    """
    bonuses = BonusFactory.create_batch(10, user=user)

    BonusFactory.create_batch(5, user=UserFactory.create())

    metrics = calculator().get_metrics(user)

    bonus = sum(bonus.sum for bonus in bonuses)
    assert metrics["bonus"] == bonus
    checkers.check_taxes(metrics, taxes=bonus * user.tax_rate)
