import pytest

from apps.core.utils.time import seconds
from apps.development.graphql.types.issue import IssueType
from apps.development.models.issue import ISSUE_STATES
from apps.development.services.issue.metrics import get_metrics
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory, SalaryFactory
from tests.test_users.factories.user import UserFactory


@pytest.fixture
def user(db):
    yield UserFactory.create(hour_rate=100)


def test_payroll_metrics(user):
    issue = IssueFactory.create(user=user, state=ISSUE_STATES.OPENED)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=-seconds(hours=3)
    )

    metrics = get_metrics(issue)

    assert metrics.payroll == 6 * user.hour_rate
    assert metrics.paid == 0


def test_paid_metrics(user):
    issue = IssueFactory.create(user=user, state=ISSUE_STATES.OPENED)
    salary = SalaryFactory.create(user=user)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=-seconds(hours=3)
    )

    metrics = get_metrics(issue)

    assert metrics.payroll == 0
    assert metrics.paid == 6 * user.hour_rate


def test_complex_metrics(user):
    issue = IssueFactory.create(user=user, state=ISSUE_STATES.OPENED)
    salary = SalaryFactory.create(user=user)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=-seconds(hours=3)
    )

    metrics = get_metrics(issue)

    assert metrics.payroll == user.hour_rate
    assert metrics.paid == 5 * user.hour_rate


def test_remains(user):
    issue_1 = IssueFactory.create(
        user=user,
        state=ISSUE_STATES.OPENED,
        time_estimate=seconds(hours=4),
        total_time_spent=seconds(hours=2),
    )
    issue_2 = IssueFactory.create(
        user=user,
        state=ISSUE_STATES.CLOSED,
        time_estimate=seconds(hours=4),
        total_time_spent=seconds(hours=8),
    )
    issue_3 = IssueFactory.create(
        user=user,
        state=ISSUE_STATES.CLOSED,
        total_time_spent=seconds(hours=3),
    )

    metrics = get_metrics(issue_1)
    assert metrics.remains == seconds(hours=2)

    metrics = get_metrics(issue_2)
    assert metrics.remains == 0

    metrics = get_metrics(issue_3)
    assert metrics.remains == 0


def test_efficiency(user):
    issue_1 = IssueFactory.create(
        user=user,
        state=ISSUE_STATES.CLOSED,
        time_estimate=seconds(hours=4),
        total_time_spent=seconds(hours=2),
    )
    issue_2 = IssueFactory.create(
        user=user,
        state=ISSUE_STATES.CLOSED,
        time_estimate=seconds(hours=4),
        total_time_spent=seconds(hours=8),
    )
    issue_3 = IssueFactory.create(
        user=user,
        state=ISSUE_STATES.OPENED,
        time_estimate=seconds(hours=4),
        total_time_spent=seconds(hours=2),
    )

    metrics = get_metrics(issue_1)
    assert metrics.efficiency == 2.0

    metrics = get_metrics(issue_2)
    assert metrics.remains == 0

    metrics = get_metrics(issue_3)
    assert metrics.efficiency is None


def test_resolver(user):
    issue = IssueFactory.create(user=user, state=ISSUE_STATES.OPENED)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=seconds(hours=6)
    )

    metrics = IssueType.resolve_metrics(issue, None)

    assert metrics.payroll == 6 * user.hour_rate
    assert metrics.paid == 0
