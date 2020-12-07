import pytest
from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.development.models.merge_request import MergeRequestState
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


def test_payroll_opened(user):  # noqa: WPS213
    """
    Test payroll opened.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.OPENED)
    mr = MergeRequestFactory.create(state=MergeRequestState.OPENED)

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
        base=mr,
        time_spent=seconds(hours=5),
    )

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


def test_payroll_opened_has_salary(user):  # noqa: WPS213
    """
    Test payroll opened has salary.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.OPENED)
    mr = MergeRequestFactory.create(state=MergeRequestState.OPENED)

    salary = SalaryFactory.create(user=user)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=4),
        salary=salary,
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

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr,
        time_spent=seconds(hours=5),
    )

    MergeRequestSpentTimeFactory.create(
        user=user,
        base=mr,
        time_spent=seconds(hours=2),
        salary=salary,
    )

    metrics = calculator().get_metrics(user)

    # check common
    checkers.check_spent(
        metrics,
        mr_opened_spent=seconds(hours=5),
        issues_opened_spent=seconds(hours=7),
    )
    checkers.check_taxes(
        metrics,
        taxes_opened=user.tax_rate * user.hour_rate * 12,
        taxes=user.hour_rate * 12 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics,
        payroll_opened=user.hour_rate * 12,
    )

    # check issues
    checkers.check_taxes(
        metrics["issues"],
        taxes_opened=user.hour_rate * 7 * user.tax_rate,
        taxes=user.hour_rate * 7 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics["issues"],
        payroll_opened=user.hour_rate * 7,
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


def test_payroll_opened_has_closed(user):  # noqa: WPS213
    """
    Test payroll opened has closed.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.CLOSED)

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
    IssueSpentTimeFactory.create(user=user, time_spent=seconds(hours=5))

    metrics = calculator().get_metrics(user)

    # check common
    checkers.check_spent(
        metrics,
        issues_closed_spent=seconds(hours=6),
        issues_opened_spent=seconds(hours=5),
    )
    checkers.check_taxes(
        metrics,
        taxes_closed=user.tax_rate * user.hour_rate * 6,
        taxes_opened=user.tax_rate * user.hour_rate * 5,
        taxes=user.hour_rate * 11 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics,
        payroll_opened=user.hour_rate * 5,
        payroll_closed=user.hour_rate * 6,
    )

    # check issues
    checkers.check_taxes(
        metrics["issues"],
        taxes_closed=user.tax_rate * user.hour_rate * 6,
        taxes_opened=user.tax_rate * user.hour_rate * 5,
        taxes=user.hour_rate * 11 * user.tax_rate,
    )
    checkers.check_payroll(
        metrics["issues"],
        payroll_opened=user.hour_rate * 5,
        payroll_closed=user.hour_rate * 6,
    )

    # check merge_request
    checkers.check_taxes(metrics["merge_requests"])
    checkers.check_payroll(metrics["merge_requests"])


def test_payroll_opened_another_user(user):  # noqa: WPS213
    """
    Test payroll opened another user.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.OPENED)

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


def test_payroll_opened_has_opened(user):  # noqa: WPS213
    """
    Test payroll opened has opened.

    :param user:
    """
    issue = IssueFactory.create(state=IssueState.OPENED)

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
