import pytest
from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.development.models.merge_request import MergeRequestState
from apps.users.services.user.metrics.main import UserMetricsProvider
from tests.test_development.factories import IssueFactory, MergeRequestFactory
from tests.test_payroll.factories import (
    IssueSpentTimeFactory,
    MergeRequestSpentTimeFactory,
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


def test_payroll_opened(user):
    """
    Test payroll opened.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.OPENED)

    _add_spents(user, issue)

    metrics = calculator().get_metrics(user)

    # check common
    checkers.check_spent(
        metrics,
        issues_opened_spent=seconds(hours=4),
        mr_opened_spent=seconds(hours=5),
    )
    checkers.check_taxes(
        metrics,
        taxes_opened=user.hour_rate * 9 * user.tax_rate,
        taxes=user.hour_rate * 9 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics,
        payroll_opened=user.hour_rate * 9,
    )

    # check issues
    checkers.check_taxes(
        metrics["issues"],
        taxes_opened=user.hour_rate * 4 * user.tax_rate,
        taxes=user.hour_rate * 4 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics["issues"],
        payroll_opened=user.hour_rate * 4,
    )

    # check merge_request
    checkers.check_taxes(
        metrics["merge_requests"],
        taxes_opened=user.hour_rate * 5 * user.tax_rate,
        taxes=user.hour_rate * 5 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics["merge_requests"],
        payroll_opened=user.hour_rate * 5,
    )


def _add_spents(user, issue) -> None:
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=1),
    )

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=-seconds(hours=2),
    )

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=5),
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=MergeRequestFactory.create(state=MergeRequestState.OPENED),
        time_spent=seconds(hours=5),
    )
