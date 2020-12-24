import pytest
from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.users.services.user.metrics.main import UserMetricsProvider
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_payroll.test_gql.test_user_metrics.test_provider import (
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


def test_payroll_opened_another_user(user):
    """
    Test payroll opened another user.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.OPENED)
    another_user = UserFactory.create()
    _add_spents(user, issue, another_user)

    metrics = calculator().get_metrics(user)

    # check common
    checkers.check_spent(
        metrics,
        issues_opened_spent=seconds(hours=5),
    )
    checkers.check_taxes(
        metrics,
        taxes_opened=user.tax_rate * user.hour_rate * 5,
        taxes=user.hour_rate * 5 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics,
        payroll_opened=user.hour_rate * 5,
    )

    # check issues
    checkers.check_taxes(
        metrics["issues"],
        taxes_opened=user.tax_rate * user.hour_rate * 5,
        taxes=user.hour_rate * 5 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics["issues"],
        payroll_opened=user.hour_rate * 5,
    )

    # check merge_request
    checkers.check_taxes(metrics["merge_requests"])
    checkers.check_payroll(metrics["merge_requests"])


def _add_spents(user, issue, another_user) -> None:
    IssueSpentTimeFactory.create(
        user=another_user,
        base=issue,
        time_spent=seconds(hours=1),
    )
    IssueSpentTimeFactory.create(
        user=another_user,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=5),
    )
