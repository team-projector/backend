from datetime import timedelta, datetime, date
from typing import Dict

from django.test import override_settings

from apps.core.utils.time import seconds
from apps.development.models.issue import ISSUE_STATES
from apps.payroll.services.metrics.progress.user import (
    get_user_progress_metrics
)
from tests.base import format_date
from tests.test_development.factories import IssueFactory


@override_settings(TP_WEEKENDS_DAYS=[])
def test_replay(user):
    IssueFactory.create(
        user=user,
        due_date=datetime.now() + timedelta(days=10),
        time_estimate=seconds(hours=15),
        total_time_spent=0,
        state=ISSUE_STATES.opened
    )

    start = datetime.now().date() + timedelta(days=1)
    end = datetime.now().date() + timedelta(days=5)
    metrics = get_user_progress_metrics(user, start, end, 'day')

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
        state=ISSUE_STATES.opened
    )

    start = datetime.now().date() + timedelta(days=1)
    end = datetime.now().date() + timedelta(days=5)
    metrics = get_user_progress_metrics(user, start, end, 'day')

    assert len(metrics) == (end - start).days + 1
    _check_metrics(metrics, {
        start: timedelta(hours=5)
    })


def _check_metrics(metrics,
                   loadings: Dict[date, timedelta]):
    loadings = _prepare_metrics(loadings)

    for metric in metrics:
        assert metric.start == metric.end

        _check_metric(metric, 'loading', loadings)


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
