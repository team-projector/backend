from apps.development.services.metrics.issue import get_issue_metrcis
from apps.development.models.issue import STATE_OPENED, STATE_CLOSED
from apps.core.utils.time import seconds
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory, SalaryFactory


def test_payroll_metrics(user):
    user.hour_rate = 100
    user.save()

    issue = IssueFactory.create(user=user, state=STATE_OPENED)

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

    metrics = get_issue_metrcis(issue)

    assert metrics.payroll == 6 * user.hour_rate
    assert metrics.paid == 0


def test_paid_metrics(user):
    user.hour_rate = 100
    user.save()

    issue = IssueFactory.create(user=user, state=STATE_OPENED)
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

    metrics = get_issue_metrcis(issue)

    assert metrics.payroll == 0
    assert metrics.paid == 6 * user.hour_rate


def test_complex_metrics(user):
    user.hour_rate = 100
    user.save()

    issue = IssueFactory.create(user=user, state=STATE_OPENED)
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

    metrics = get_issue_metrcis(issue)

    assert metrics.payroll == user.hour_rate
    assert metrics.paid == 5 * user.hour_rate


def test_remains(user):
    issue_1 = IssueFactory.create(
        user=user,
        state=STATE_OPENED,
        time_estimate=seconds(hours=4),
        total_time_spent=seconds(hours=2),
    )
    issue_2 = IssueFactory.create(
        user=user,
        state=STATE_CLOSED,
        time_estimate=seconds(hours=4),
        total_time_spent=seconds(hours=8),
    )
    issue_3 = IssueFactory.create(
        user=user,
        state=STATE_CLOSED,
        total_time_spent=seconds(hours=3),
    )

    metrics = get_issue_metrcis(issue_1)
    assert metrics.remains == seconds(hours=2)

    metrics = get_issue_metrcis(issue_2)
    assert metrics.remains == 0

    metrics = get_issue_metrcis(issue_3)
    assert metrics.remains == 0


def test_efficiency(user):
    issue_1 = IssueFactory.create(
        user=user,
        state=STATE_CLOSED,
        time_estimate=seconds(hours=4),
        total_time_spent=seconds(hours=2),
    )
    issue_2 = IssueFactory.create(
        user=user,
        state=STATE_CLOSED,
        time_estimate=seconds(hours=4),
        total_time_spent=seconds(hours=8),
    )
    issue_3 = IssueFactory.create(
        user=user,
        state=STATE_OPENED,
        time_estimate=seconds(hours=4),
        total_time_spent=seconds(hours=2),
    )

    metrics = get_issue_metrcis(issue_1)
    assert metrics.efficiency == 2.0

    metrics = get_issue_metrcis(issue_2)
    assert metrics.remains == 0

    metrics = get_issue_metrcis(issue_3)
    assert metrics.efficiency is None
