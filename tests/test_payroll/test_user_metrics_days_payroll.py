from datetime import date, timedelta, datetime
from typing import Dict

from django.test import override_settings
from django.utils import timezone

from apps.core.utils.date import begin_of_week
from apps.development.models.issue import STATE_CLOSED, STATE_OPENED
from apps.payroll.services.metrics.progress.user import \
    get_user_progress_metrics
from tests.base import format_date
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory, SalaryFactory


@override_settings(TP_WEEKENDS_DAYS=[])
def test_opened(user):
    user.hour_rate = 100
    user.save()

    issue = IssueFactory.create(user=user, due_date=datetime.now())

    monday = begin_of_week(timezone.now().date())

    IssueSpentTimeFactory.create(
        date=monday,
        user=user,
        base=issue,
        time_spent=timedelta(hours=3).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=user,
        base=issue,
        time_spent=timedelta(hours=2).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=user,
        base=issue,
        time_spent=timedelta(hours=4).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=user,
        base=issue,
        time_spent=-timedelta(hours=3).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=10),
        user=user,
        base=issue,
        time_spent=-timedelta(hours=3).total_seconds()
    )

    issue.state = STATE_OPENED
    issue.save()

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_user_progress_metrics(user, start, end, 'day')

    _check_metrics(metrics,
                   {
                       monday: 3 * user.hour_rate,
                       monday + timedelta(days=1): user.hour_rate,
                       monday + timedelta(days=2): 2 * user.hour_rate
                   }, {
                       monday: 0
                   })


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
        time_spent=timedelta(hours=3).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=user,
        base=issue,
        salary=salary,
        time_spent=timedelta(hours=2).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=user,
        base=issue,
        salary=salary,
        time_spent=timedelta(hours=4).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=user,
        base=issue,
        salary=salary,
        time_spent=-timedelta(hours=3).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=10),
        user=user,
        base=issue,
        salary=salary,
        time_spent=-timedelta(hours=3).total_seconds()
    )

    issue.state = STATE_CLOSED
    issue.save()

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_user_progress_metrics(user, start, end, 'day')

    _check_metrics(metrics,
                   {
                       monday: 0
                   }, {
                       monday: 3 * user.hour_rate,
                       monday + timedelta(days=1): user.hour_rate,
                       monday + timedelta(days=2): 2 * user.hour_rate
                   })


@override_settings(TP_WEEKENDS_DAYS=[])
def test_closed(user):
    user.hour_rate = 100
    user.save()

    issue = IssueFactory.create(user=user, due_date=datetime.now())
    monday = begin_of_week(timezone.now().date())

    IssueSpentTimeFactory.create(
        date=monday,
        user=user,
        base=issue,
        time_spent=timedelta(hours=3).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=user,
        base=issue,
        time_spent=timedelta(hours=2).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=user,
        base=issue,
        time_spent=timedelta(hours=4).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=user,
        base=issue,
        time_spent=-timedelta(hours=3).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=10),
        user=user,
        base=issue,
        time_spent=-timedelta(hours=3).total_seconds()
    )

    issue.state = STATE_CLOSED
    issue.save()

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_user_progress_metrics(user, start, end, 'day')

    _check_metrics(metrics,
                   {
                       monday: 3 * user.hour_rate,
                       monday + timedelta(days=1): user.hour_rate,
                       monday + timedelta(days=2): 2 * user.hour_rate
                   }, {
                       monday: 0
                   })


@override_settings(TP_WEEKENDS_DAYS=[])
def test_complex(user):
    user.hour_rate = 100
    user.save()

    monday = begin_of_week(timezone.now().date())

    salary = SalaryFactory.create(user=user)

    closed_issue = IssueFactory.create(user=user, due_date=datetime.now(), state=STATE_CLOSED)
    opened_issue = IssueFactory.create(user=user, due_date=datetime.now(), state=STATE_OPENED)

    IssueSpentTimeFactory.create(
        date=monday,
        user=user,
        base=closed_issue,
        time_spent=timedelta(hours=4).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday,
        user=user,
        base=opened_issue,
        time_spent=timedelta(hours=2).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=2, hours=5),
        user=user,
        base=opened_issue,
        time_spent=timedelta(hours=2).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1),
        user=user,
        base=opened_issue,
        time_spent=timedelta(hours=4).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=1, hours=5),
        user=user,
        base=closed_issue,
        salary=salary,
        time_spent=timedelta(hours=3).total_seconds()
    )
    IssueSpentTimeFactory.create(
        date=monday + timedelta(days=10),
        user=user,
        base=opened_issue,
        time_spent=-timedelta(hours=3).total_seconds()
    )

    start = monday - timedelta(days=5)
    end = monday + timedelta(days=5)
    metrics = get_user_progress_metrics(user, start, end, 'day')

    _check_metrics(metrics,
                   {
                       monday: 6 * user.hour_rate,
                       monday + timedelta(days=1): 4 * user.hour_rate,
                       monday + timedelta(days=2): 2 * user.hour_rate,
                   }, {
                       monday + timedelta(days=1): 3 * user.hour_rate,
                   })


def _check_metrics(metrics,
                   payroll: Dict[date, float],
                   paid: Dict[date, float]):
    payroll = _prepare_metrics(payroll)
    paid = _prepare_metrics(paid)

    for metric in metrics:
        assert metric.start == metric.end

        _check_metric(metric, 'payroll', payroll)
        _check_metric(metric, 'paid', paid)


def _prepare_metrics(metrics):
    return {
        format_date(d): time
        for d, time in metrics.items()
    }


def _check_metric(metric, metric_name, values):
    start_dt = str(metric.start)

    if start_dt in values:
        assert getattr(metric, metric_name) == values[start_dt]
    else:
        assert getattr(metric, metric_name) == 0
