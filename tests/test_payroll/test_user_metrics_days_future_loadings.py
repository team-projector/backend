from datetime import date, datetime, timedelta
from typing import Dict

from django.test import override_settings

from apps.core.utils.time import seconds
from apps.development.models.issue import ISSUE_STATES
from apps.users.services.user.metrics import get_progress_metrics
from tests.helpers.base import format_date
from tests.test_development.factories import IssueFactory


@override_settings(TP_WEEKENDS_DAYS=[])
def test_replay(user):
    IssueFactory.create(
        user=user,
        due_date=datetime.now() + timedelta(days=10),
        time_estimate=seconds(hours=15),
        total_time_spent=0,
        state=ISSUE_STATES.OPENED
    )

    start = datetime.now().date() + timedelta(days=1)
    end = datetime.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(user, start, end, "day")

    assert len(metrics) == (end - start).days + 1
    _check_metrics(metrics, {
        start: timedelta(hours=7)
    })


@override_settings(TP_WEEKENDS_DAYS=[])
def test_has_spents(user):
    IssueFactory.create(
        user=user,
        due_date=datetime.now() + timedelta(days=10),
        time_estimate=seconds(hours=15),
        total_time_spent=seconds(hours=2),
        state=ISSUE_STATES.OPENED
    )

    start = datetime.now().date() + timedelta(days=1)
    end = datetime.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(user, start, end, "day")

    assert len(metrics) == (end - start).days + 1
    _check_metrics(metrics, {
        start: timedelta(hours=5)
    })


@override_settings(TP_WEEKENDS_DAYS=[])
def test_replay_without_active_issues(user):
    IssueFactory.create(
        user=user,
        due_date=datetime.now() + timedelta(days=10),
        time_estimate=seconds(hours=3),
        total_time_spent=3,
        state=ISSUE_STATES.CLOSED
    )

    start = datetime.now().date() + timedelta(days=1)
    end = datetime.now().date() + timedelta(days=3)
    metrics = get_progress_metrics(user, start, end, "day")

    assert len(metrics) == (end - start).days + 1
    _check_metrics(metrics, {
        start: timedelta(seconds=0)
    })


@override_settings(TP_WEEKENDS_DAYS=[0, 1, 2, 3, 4, 5, 6])
def test_not_apply_loading_weekends(user):
    IssueFactory.create(
        user=user,
        due_date=datetime.now() + timedelta(days=10),
        time_estimate=seconds(hours=15),
        total_time_spent=0,
        state=ISSUE_STATES.OPENED
    )

    start = datetime.now().date() + timedelta(days=1)
    end = datetime.now().date() + timedelta(days=5)
    metrics = get_progress_metrics(user, start, end, "day")

    assert len(metrics) == (end - start).days + 1
    _check_metrics(metrics, {
        start: timedelta(seconds=0)
    })


def _check_metrics(metrics,
                   loadings: Dict[date, timedelta]):
    loadings = _prepare_metrics(loadings)

    for metric in metrics:
        assert metric.start == metric.end

        _check_metric(metric, "loading", loadings)


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
