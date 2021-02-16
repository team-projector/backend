import pytest
from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.users.logic.services.user.metrics import UserMetricsService
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_payroll.test_gql.test_user_metrics.test_provider import (
    checkers,
)
from tests.test_users.factories.user import UserFactory

calculator = UserMetricsService


@pytest.fixture()
def user(db):
    """
    User.

    :param db:
    """
    return UserFactory.create(login="user", hour_rate=100, tax_rate=15)


def test_payroll_opened_has_opened(user):
    """
    Test payroll opened has opened.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.OPENED)
    _add_spents(user, issue)

    metrics = calculator().get_metrics(user)

    # check common
    checkers.check_spent(
        metrics,
        issues_closed_spent=seconds(hours=5),
        issues_opened_spent=seconds(hours=6),
    )
    checkers.check_taxes(
        metrics,
        taxes_closed=user.tax_rate * user.hour_rate * 5,
        taxes_opened=user.tax_rate * user.hour_rate * 6,
        taxes=user.hour_rate * 11 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics,
        payroll_closed=user.hour_rate * 5,
        payroll_opened=user.hour_rate * 6,
    )

    # check issues
    checkers.check_taxes(
        metrics["issues"],
        taxes_closed=user.tax_rate * user.hour_rate * 5,
        taxes_opened=user.tax_rate * user.hour_rate * 6,
        taxes=user.hour_rate * 11 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics["issues"],
        payroll_closed=user.hour_rate * 5,
        payroll_opened=user.hour_rate * 6,
    )

    # check merge_request
    checkers.check_taxes(metrics["merge_requests"])
    checkers.check_payroll(metrics["merge_requests"])


def _add_spents(user, issue) -> None:
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
        base=IssueFactory.create(state=IssueState.CLOSED),
        time_spent=seconds(hours=5),
    )
