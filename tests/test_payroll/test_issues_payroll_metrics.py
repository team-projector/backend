from datetime import timedelta

from apps.development.services.metrics.issue import get_issue_metrcis
from apps.development.models.issue import STATE_OPENED
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory, SalaryFactory


def test_payroll_metrics(user):
    user.hour_rate = 100
    user.save()

    issue = IssueFactory.create(user=user, state=STATE_OPENED)

    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=timedelta(hours=3).total_seconds()
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=timedelta(hours=2).total_seconds()
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=timedelta(hours=4).total_seconds()
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=-timedelta(hours=3).total_seconds()
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
        time_spent=timedelta(hours=3).total_seconds()
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=timedelta(hours=2).total_seconds()
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=timedelta(hours=4).total_seconds()
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=-timedelta(hours=3).total_seconds()
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
        time_spent=timedelta(hours=3).total_seconds()
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        salary=salary,
        time_spent=timedelta(hours=2).total_seconds()
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=timedelta(hours=4).total_seconds()
    )
    IssueSpentTimeFactory.create(
        user=user,
        base=issue,
        time_spent=-timedelta(hours=3).total_seconds()
    )

    metrics = get_issue_metrcis(issue)

    assert metrics.payroll == user.hour_rate
    assert metrics.paid == 5 * user.hour_rate
