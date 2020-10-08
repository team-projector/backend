import pytest
from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.development.services.issue.metrics import get_issue_metrics
from tests.test_development.factories import IssueFactory
from tests.test_development.test_services.test_issues.test_metrics import (
    checkers,
)
from tests.test_payroll.factories import IssueSpentTimeFactory, SalaryFactory
from tests.test_users.factories.user import UserFactory


@pytest.fixture()
def user(db):
    """
    User.

    :param db:
    """
    return UserFactory.create(hour_rate=100, tax_rate=15)


def test_payroll_metrics(user):
    """
    Test payroll metrics.

    :param user:
    """
    issue = IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=6),
        total_time_spent=seconds(hours=6),
    )

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    checkers.check_issues_metrics(
        get_issue_metrics(issue),
        payroll=6 * user.hour_rate,
        paid=0,
    )


def test_paid_metrics(user):
    """
    Test paid metrics.

    :param user:
    """
    issue = IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=6),
        total_time_spent=seconds(hours=6),
    )
    salary = SalaryFactory.create(user=user)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=-seconds(hours=3),
    )

    checkers.check_issues_metrics(
        get_issue_metrics(issue),
        paid=6 * user.hour_rate,
    )


def test_complex_metrics(user):
    """
    Test complex metrics.

    :param user:
    """
    issue = IssueFactory.create(
        user=user,
        time_estimate=seconds(hours=6),
        total_time_spent=seconds(hours=6),
    )
    salary = SalaryFactory.create(user=user)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    checkers.check_issues_metrics(
        get_issue_metrics(issue),
        payroll=user.hour_rate,
        paid=5 * user.hour_rate,
    )


def test_remains(user):
    """
    Test remains.

    :param user:
    """
    issues = [
        IssueFactory.create(
            user=user,
            time_estimate=seconds(hours=4),
            total_time_spent=seconds(hours=2),
        ),
        IssueFactory.create(
            user=user,
            state=IssueState.CLOSED,
            time_estimate=seconds(hours=4),
            total_time_spent=seconds(hours=8),
        ),
        IssueFactory.create(
            user=user,
            state=IssueState.CLOSED,
            time_estimate=seconds(hours=4),
            total_time_spent=seconds(hours=3),
        ),
    ]

    metrics = get_issue_metrics(issues[0])
    assert metrics.remains == seconds(hours=2)

    metrics = get_issue_metrics(issues[1])
    assert metrics.remains == -seconds(hours=4)

    metrics = get_issue_metrics(issues[2])
    assert metrics.remains == seconds(hours=1)


def test_efficiency(user):
    """
    Test efficiency.

    :param user:
    """
    issues = [
        IssueFactory.create(
            user=user,
            state=IssueState.CLOSED,
            time_estimate=seconds(hours=4),
            total_time_spent=seconds(hours=2),
        ),
        IssueFactory.create(
            user=user,
            state=IssueState.CLOSED,
            time_estimate=seconds(hours=4),
            total_time_spent=seconds(hours=8),
        ),
        IssueFactory.create(
            user=user,
            state=IssueState.OPENED,
            time_estimate=seconds(hours=4),
            total_time_spent=seconds(hours=2),
        ),
    ]

    metrics = get_issue_metrics(issues[0])
    assert metrics.efficiency == 2.0

    metrics = get_issue_metrics(issues[1])
    assert metrics.remains == -seconds(hours=4)

    metrics = get_issue_metrics(issues[2])
    assert metrics.efficiency == 0
