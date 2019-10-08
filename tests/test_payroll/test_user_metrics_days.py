from datetime import timedelta, datetime
from typing import Dict

from django.db.models import Sum
from django.test import override_settings
from django.utils import timezone
from pytest import raises

from apps.core.utils.time import seconds
from apps.development.models.issue import ISSUE_STATES
from apps.users.services import user as user_service
from tests.base import format_date
from tests.test_development.factories import IssueFactory
from tests.test_payroll.factories import IssueSpentTimeFactory
from tests.test_users.factories import UserFactory


@override_settings(TP_WEEKENDS_DAYS=[])
def test_simple(user):
    issue = IssueFactory.create(user=user, due_date=datetime.now())

    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=4),
        user=user,
        base=issue,
        time_spent=seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=2, hours=5),
        user=user,
        base=issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=1),
        user=user,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=1, hours=5),
        user=user,
        base=issue,
        time_spent=-seconds(hours=3)
    )

    issue.time_estimate = seconds(hours=15)
    issue.total_time_spent = \
        issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
    issue.state = ISSUE_STATES.opened
    issue.due_date = datetime.now() + timedelta(days=1)
    issue.save()

    start = datetime.now().date() - timedelta(days=5)
    end = datetime.now().date() + timedelta(days=5)
    metrics = user_service.get_progress_metrics(user, start, end, 'day')

    assert len(metrics) == (end - start).days + 1
    _check_metrics(metrics,
                   {
                       datetime.now() - timedelta(days=4): timedelta(hours=3),
                       datetime.now() - timedelta(days=2): timedelta(hours=2),
                       datetime.now() - timedelta(days=1): timedelta(hours=1),
                   }, {
                       datetime.now(): timedelta(hours=8),
                       datetime.now() + timedelta(days=1): timedelta(hours=1),
                   }, {
                       datetime.now() + timedelta(days=1): 1
                   }, {
                       datetime.now() + timedelta(days=1): timedelta(hours=15)
                   }, {
                       datetime.now() + timedelta(days=1):
                           timedelta(
                               seconds=issue.time_estimate - issue.total_time_spent)
                   })


@override_settings(TP_WEEKENDS_DAYS=[])
def test_negative_remains(user):
    issue = IssueFactory.create(user=user, due_date=datetime.now())
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=4),
        user=user,
        base=issue,
        time_spent=seconds(hours=3)
    )

    issue.time_estimate = seconds(hours=2)
    issue.total_time_spent = \
        issue.time_spents.aggregate(spent=Sum('time_spent'))['spent']
    issue.state = ISSUE_STATES.opened
    issue.due_date = datetime.now() + timedelta(days=1)
    issue.save()

    start = datetime.now().date() - timedelta(days=5)
    end = datetime.now().date() + timedelta(days=5)
    metrics = user_service.get_progress_metrics(user, start, end, 'day')

    assert len(metrics) == (end - start).days + 1
    _check_metrics(metrics,
                   {
                       timezone.now() - timedelta(days=4): timedelta(hours=3),
                   }, {}, {
                       timezone.now() + timedelta(days=1): 1
                   }, {
                       timezone.now() + timedelta(days=1): timedelta(hours=2)
                   }, {})


@override_settings(TP_WEEKENDS_DAYS=[])
def test_loading_day_already_has_spends(user):
    issue = IssueFactory.create(user=user, due_date=datetime.now())
    issue_2 = IssueFactory.create(user=user,
                                  state=ISSUE_STATES.opened,
                                  total_time_spent=seconds(hours=3),
                                  time_estimate=seconds(hours=10))

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue_2,
        time_spent=seconds(hours=1)
    )
    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue_2,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue,
        time_spent=seconds(hours=3)
    )

    issue.time_estimate = int(seconds(hours=4))
    issue.total_time_spent = int(seconds(hours=3))
    issue.state = ISSUE_STATES.opened
    issue.due_date = datetime.now()
    issue.save()

    issue_2.total_time_spent = \
        issue_2.time_spents.aggregate(spent=Sum('time_spent'))['spent']
    issue_2.save()

    start = datetime.now().date() - timedelta(days=5)
    end = datetime.now().date() + timedelta(days=5)
    metrics = user_service.get_progress_metrics(user, start, end, 'day')

    assert len(metrics) == (end - start).days + 1
    _check_metrics(metrics,
                   {
                       timezone.now(): timedelta(hours=6)
                   }, {
                       timezone.now(): timedelta(hours=8),
                       timezone.now() + timedelta(days=1): timedelta(hours=6),
                   }, {
                       timezone.now(): 1,
                   }, {
                       timezone.now(): timedelta(hours=4),
                   }, {
                       timezone.now(): timedelta(
                           seconds=issue.time_estimate - issue.total_time_spent)
                   })


@override_settings(TP_WEEKENDS_DAYS=[])
def test_not_in_range(user):
    issue = IssueFactory.create(user=user, due_date=datetime.now())
    issue.time_estimate = 0
    issue.total_time_spent = 0
    issue.state = ISSUE_STATES.opened
    issue.save()

    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=5, hours=5),
        user=user,
        base=issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=1),
        user=user,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=1, hours=5),
        user=user,
        base=issue,
        time_spent=-seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() + timedelta(days=1),
        user=user,
        base=issue,
        time_spent=seconds(hours=3)
    )

    start = datetime.now().date() - timedelta(days=3)
    end = datetime.now().date() + timedelta(days=3)
    metrics = user_service.get_progress_metrics(user, start, end, 'day')

    assert len(metrics) == (end - start).days + 1
    _check_metrics(metrics,
                   {
                       timezone.now() - timedelta(days=1): timedelta(hours=1),
                       timezone.now() + timedelta(days=1): timedelta(hours=3)
                   }, {}, {
                       timezone.now(): 1
                   }, {}, {})


@override_settings(TP_WEEKENDS_DAYS=[])
def test_another_user(user):
    issue = IssueFactory.create(user=user, due_date=datetime.now())
    issue.time_estimate = 0
    issue.total_time_spent = 0
    issue.state = ISSUE_STATES.opened
    issue.save()

    another_user = UserFactory.create()

    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=2, hours=5),
        user=user,
        base=issue,
        time_spent=seconds(hours=2)
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=1),
        user=another_user,
        base=issue,
        time_spent=seconds(hours=4)
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() - timedelta(days=1, hours=5),
        user=user,
        base=issue,
        time_spent=-seconds(hours=3)
    )
    IssueSpentTimeFactory.create(
        date=datetime.now() + timedelta(days=1),
        user=another_user,
        base=issue,
        time_spent=seconds(hours=3)
    )

    start = datetime.now().date() - timedelta(days=5)
    end = datetime.now().date() + timedelta(days=5)
    metrics = user_service.get_progress_metrics(user, start, end, 'day')

    assert len(metrics) == (end - start).days + 1
    _check_metrics(metrics,
                   {
                       timezone.now() - timedelta(days=2): timedelta(hours=2),
                       timezone.now() - timedelta(days=1): -timedelta(hours=3)
                   }, {}, {
                       timezone.now(): 1
                   }, {}, {})


@override_settings(TP_WEEKENDS_DAYS=[])
def test_not_loading_over_daily_work_hours(user):
    user.daily_work_hours = 4
    user.save()

    issue = IssueFactory.create(
        user=user,
        due_date=datetime.now() + timedelta(days=7),
        time_estimate=seconds(hours=15),
        total_time_spent=5,
        state=ISSUE_STATES.opened
    )

    IssueSpentTimeFactory.create(
        date=datetime.now(),
        user=user,
        base=issue,
        time_spent=seconds(hours=5)
    )

    start = datetime.now().date() - timedelta(days=1)
    end = datetime.now().date() + timedelta(days=1)
    metrics = user_service.get_progress_metrics(user, start, end, 'day')

    assert len(metrics) == (end - start).days + 1
    _check_metrics(metrics,
                   {
                       timezone.now() - timedelta(days=1): timedelta(hours=0),
                       timezone.now(): timedelta(hours=5),
                   }, {
                       timezone.now(): timedelta(hours=5),
                       timezone.now() + timedelta(days=1): timedelta(hours=4),
                   }, {
                       timezone.now() + timedelta(days=7): 1
                   }, {
                       timezone.now() + timedelta(days=7): timedelta(hours=15)
                   }, {}, 4)


def test_bad_group(user):
    with raises(ValueError):
        user_service.get_progress_metrics(
            user,
            datetime.now().date() - timedelta(days=5),
            datetime.now().date() + timedelta(days=5),
            'test_bad_group'
        )


def test_provider_not_implemented(user):
    with raises(NotImplementedError):
        user_service.ProgressMetricsProvider(
            user,
            datetime.now().date() - timedelta(days=5),
            datetime.now().date() + timedelta(days=5),
        ).get_metrics()


def _check_metrics(metrics,
                   spents: Dict[datetime, timedelta],
                   loadings: Dict[datetime, timedelta],
                   issues_counts: Dict[datetime, int],
                   time_estimates: Dict[datetime, timedelta],
                   time_remains: Dict[datetime, timedelta],
                   planned_work_hours: int = 8):
    spents = _prepare_metrics(spents)
    loadings = _prepare_metrics(loadings)
    time_estimates = _prepare_metrics(time_estimates)
    issues_counts = _prepare_metrics(issues_counts)
    time_remains = _prepare_metrics(time_remains)

    for metric in metrics:
        assert metric.start == metric.end
        assert metric.planned_work_hours == planned_work_hours

        _check_metric(metric, 'time_spent', spents)
        _check_metric(metric, 'time_estimate', time_estimates)
        _check_metric(metric, 'loading', loadings)
        _check_metric(metric, 'time_remains', time_remains)

        if str(metric.start) in issues_counts:
            assert metric.issues_count == issues_counts[str(metric.start)]
        else:
            assert metric.issues_count == 0


def _prepare_metrics(metrics):
    return {
        format_date(d): time
        for d, time in metrics.items()
    }


def _check_metric(metric, metric_name, values):
    dt = str(metric.start)

    if dt in values:
        assert getattr(metric, metric_name) == values[dt].total_seconds()
    else:
        assert getattr(metric, metric_name) == 0
