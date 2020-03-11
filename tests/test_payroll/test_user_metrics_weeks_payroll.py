from datetime import date, datetime, timedelta
from typing import Dict

from django.test import override_settings
from django.utils import timezone

from apps.core.utils.date import begin_of_week
from apps.core.utils.time import seconds
from apps.development.models.issue import IssueState
from apps.users.services.user.metrics import get_progress_metrics
from tests.helpers.base import format_date
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory, SalaryFactory


@override_settings(TP_WEEKENDS_DAYS=[])
def test_opened(user):
    user.hour_rate = 100
    user.save()

    issue = IssueFactory.create(user=user, due_date=datetime.now())
    monday = begin_of_week(timezone.now().date())

    IssueSpentTimeFactory.create(
        date=monday, user=user, base=issue, time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=user,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=user,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=user,
        base=issue,
        time_spent=-seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=10),
        user=user,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    issue.state = IssueState.OPENED
    issue.save()

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_progress_metrics(user, start, end, "week")

    _check_metrics(metrics, {monday: 6 * user.hour_rate}, {monday: 0})


@override_settings(TP_WEEKENDS_DAYS=[])
def test_paid(user):
    user.hour_rate = 100
    user.save()

    issue = IssueFactory.create(user=user, due_date=datetime.now())
    monday = begin_of_week(timezone.now().date())

    salary = SalaryFactory.create(user=user)

    IssueSpentTimeFactory.create(
        date=monday,
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=user,
        base=issue,
        salary=salary,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=user,
        base=issue,
        salary=salary,
        time_spent=-seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=10),
        user=user,
        base=issue,
        salary=salary,
        time_spent=-seconds(hours=3),
    )

    issue.state = IssueState.CLOSED
    issue.save()

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_progress_metrics(user, start, end, "week")

    _check_metrics(metrics, {monday: 0}, {monday: 6 * user.hour_rate})


@override_settings(TP_WEEKENDS_DAYS=[])
def test_closed(user):
    user.hour_rate = 100
    user.save()

    issue = IssueFactory.create(user=user, due_date=datetime.now())
    monday = begin_of_week(timezone.now().date())

    IssueSpentTimeFactory.create(
        date=monday, user=user, base=issue, time_spent=seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=user,
        base=issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=user,
        base=issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=user,
        base=issue,
        time_spent=-seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=10),
        user=user,
        base=issue,
        time_spent=-seconds(hours=3),
    )

    issue.state = IssueState.CLOSED
    issue.save()

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_progress_metrics(user, start, end, "week")

    _check_metrics(metrics, {monday: 6 * user.hour_rate}, {monday: 0})


@override_settings(TP_WEEKENDS_DAYS=[])
def test_complex(user):
    user.hour_rate = 100
    user.save()

    monday = begin_of_week(timezone.now().date())

    salary = SalaryFactory.create(user=user)

    closed_issue = IssueFactory.create(
        user=user, due_date=datetime.now(), state=IssueState.CLOSED
    )
    opened_issue = IssueFactory.create(
        user=user, due_date=datetime.now(), state=IssueState.OPENED
    )

    IssueSpentTimeFactory.create(
        date=monday, user=user, base=closed_issue, time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=monday, user=user, base=opened_issue, time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=user,
        base=opened_issue,
        time_spent=seconds(hours=2),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=user,
        base=opened_issue,
        time_spent=seconds(hours=4),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=user,
        salary=salary,
        base=closed_issue,
        time_spent=seconds(hours=3),
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=10),
        user=user,
        base=opened_issue,
        time_spent=-seconds(hours=3),
    )

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_progress_metrics(user, start, end, "week")

    _check_metrics(
        metrics, {monday: 12 * user.hour_rate}, {monday: 3 * user.hour_rate}
    )


def _check_metrics(
    metrics, payroll: Dict[date, float], paid: Dict[date, float]
):
    payroll = _prepare_metrics(payroll)
    paid = _prepare_metrics(paid)

    for metric in metrics:
        assert metric.end == metric.start + timedelta(weeks=1)

        _check_metric(metric, "payroll", payroll)
        _check_metric(metric, "paid", paid)


def _prepare_metrics(metrics):
    return {
        format_date(metric_date): time for metric_date, time in metrics.items()
    }


def _check_metric(metric, metric_name, values):
    start_dt = values.get(str(metric.start))

    if start_dt:
        assert getattr(metric, metric_name) == start_dt
    else:
        assert getattr(metric, metric_name) == 0
