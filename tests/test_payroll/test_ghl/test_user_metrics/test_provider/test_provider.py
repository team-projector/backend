from datetime import timedelta

import pytest
from django.utils import timezone
from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.users.services.user import metrics
from apps.users.services.user.metrics.main import UserMetricsProvider
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import (
    BonusFactory,
    IssueSpentTimeFactory,
    PenaltyFactory,
    SalaryFactory,
)
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


def test_last_salary_date(user, ghl_auth_mock_info):
    """
    Test last salary date.

    :param user:
    :param ghl_auth_mock_info:
    """
    SalaryFactory(
        user=user,
        period_to=timezone.now() - timedelta(days=30),
        payed=True,
    )
    salary = SalaryFactory(user=user, period_to=timezone.now())

    last_salary_date = metrics.last_salary_date_resolver(user)
    assert last_salary_date == salary.period_to.date()


def test_complex(user):
    """
    Test complex.

    :param user:
    """
    BonusFactory.create_batch(10, sum=100, user=user)
    PenaltyFactory.create_batch(10, sum=50, user=user)

    issue = IssueFactory.create(user=user, state=IssueState.OPENED)
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=IssueFactory.create(user=user, state=IssueState.CLOSED),
        time_spent=seconds(hours=5),
    )

    metrics = calculator().get_metrics(user)

    # check common
    bonus, penalty = 100 * 10, 50 * 10
    assert metrics["bonus"] == bonus
    assert metrics["penalty"] == penalty

    checkers.check_spent(
        metrics,
        issues_closed_spent=seconds(hours=5),
        issues_opened_spent=seconds(hours=6),
    )
    checkers.check_payroll(
        metrics,
        payroll_closed=user.hour_rate * 5,
        payroll_opened=user.hour_rate * 6,
    )
    checkers.check_taxes(
        metrics,
        taxes_closed=user.tax_rate * user.hour_rate * 5,
        taxes_opened=user.tax_rate * user.hour_rate * 6,
        taxes=(user.hour_rate * 11 + bonus - penalty) * user.tax_rate,
    )

    # check issues
    checkers.check_payroll(
        metrics["issues"],
        payroll_closed=user.hour_rate * 5,
        payroll_opened=user.hour_rate * 6,
    )
    checkers.check_taxes(
        metrics["issues"],
        taxes_closed=user.tax_rate * user.hour_rate * 5,
        taxes_opened=user.tax_rate * user.hour_rate * 6,
        taxes=user.hour_rate * 11 * user.tax_rate,
    )

    # check merge_request
    checkers.check_taxes(metrics["merge_requests"])
    checkers.check_payroll(metrics["merge_requests"])
