import pytest
from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.users.services.user.metrics.main import UserMetricsProvider
from tests.test_development.factories import IssueFactory, MergeRequestFactory
from tests.test_payroll.factories import (
    IssueSpentTimeFactory,
    MergeRequestSpentTimeFactory,
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


def test_payroll_closed(user):
    """
    Test payroll closed.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.CLOSED)

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

    metrics = calculator().get_metrics(user)

    checkers.check_spent(
        metrics,
        issues_closed_spent=seconds(hours=4),
    )
    checkers.check_taxes(
        metrics,
        taxes_closed=user.tax_rate * user.hour_rate * 4,
        taxes=user.hour_rate * 4 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics,
        payroll_closed=user.hour_rate * 4,
    )

    checkers.check_taxes(
        metrics["issues"],
        taxes_closed=user.tax_rate * user.hour_rate * 4,
        taxes=user.hour_rate * 4 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics["issues"],
        payroll_closed=user.hour_rate * 4,
    )

    checkers.check_taxes(metrics["merge_requests"])
    checkers.check_payroll(metrics["merge_requests"])


def test_payroll_closed_has_salary(user):
    """
    Test payroll closed has salary.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.CLOSED)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=4),
        salary=SalaryFactory.create(user=user),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=5),
    )

    metrics = calculator().get_metrics(user)

    checkers.check_spent(
        metrics,
        issues_closed_spent=seconds(hours=7),
    )
    checkers.check_taxes(
        metrics,
        taxes_closed=user.tax_rate * user.hour_rate * 7,
        taxes=user.hour_rate * 7 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics,
        payroll_closed=user.hour_rate * 7,
    )

    checkers.check_taxes(
        metrics["issues"],
        taxes_closed=user.tax_rate * user.hour_rate * 7,
        taxes=user.hour_rate * 7 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics["issues"],
        payroll_closed=user.hour_rate * 7,
    )

    checkers.check_taxes(metrics["merge_requests"])
    checkers.check_payroll(metrics["merge_requests"])


def test_payroll_closed_another_user(user):
    """
    Test payroll closed another user.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.CLOSED)
    mr = MergeRequestFactory.create(state=IssueState.CLOSED)

    another_user = UserFactory.create()

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

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr,
        time_spent=seconds(hours=2),
    )

    metrics = calculator().get_metrics(user)

    checkers.check_spent(
        metrics,
        issues_closed_spent=seconds(hours=5),
        mr_closed_spent=seconds(hours=2),
    )
    checkers.check_taxes(
        metrics,
        taxes_closed=user.tax_rate * user.hour_rate * 7,
        taxes=user.hour_rate * 7 * user.tax_rate,
    )
    checkers.check_payroll(metrics, payroll_closed=user.hour_rate * 7)

    checkers.check_taxes(
        metrics["issues"],
        taxes_closed=user.tax_rate * user.hour_rate * 5,
        taxes=user.hour_rate * 5 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics["issues"],
        payroll_closed=user.hour_rate * 5,
    )

    checkers.check_taxes(
        metrics["merge_requests"],
        taxes_closed=user.tax_rate * user.hour_rate * 2,
        taxes=user.hour_rate * 2 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics["merge_requests"],
        payroll_closed=user.hour_rate * 2,
    )
