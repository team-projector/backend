# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from typing import Dict

from apps.users.services.user.metrics import UserProgressMetricsList
from tests.helpers.base import format_date


def check_user_progress_metrics(
    metrics: UserProgressMetricsList,
    spents: Dict[datetime, timedelta] = None,
    loadings: Dict[datetime, timedelta] = None,
    issues_counts: Dict[datetime, int] = None,
    time_estimates: Dict[datetime, timedelta] = None,
    time_remains: Dict[datetime, timedelta] = None,
    planned_work_hours: int = 8,
):
    """Check user progress metrics."""
    spents = _prepare_metrics(spents)
    loadings = _prepare_metrics(loadings)
    time_estimates = _prepare_metrics(time_estimates)
    issues_counts = _prepare_metrics(issues_counts)
    time_remains = _prepare_metrics(time_remains)

    for metric in metrics:
        assert metric.start == metric.end
        assert metric.planned_work_hours == planned_work_hours

        _check_metric(metric, "time_spent", spents)
        _check_metric(metric, "time_estimate", time_estimates)
        _check_metric(metric, "loading", loadings)
        _check_metric(metric, "time_remains", time_remains)

        if str(metric.start) in issues_counts:
            assert metric.issues_count == issues_counts.get(str(metric.start))
        else:
            assert metric.issues_count == 0


def _prepare_metrics(metrics):
    if metrics is None:
        return {}

    return {
        format_date(metric_date): time for metric_date, time in metrics.items()
    }


def _check_metric(metric, metric_name, values):
    dt = str(metric.start)

    if dt in values:
        assert getattr(metric, metric_name) == values.get(dt).total_seconds()
    else:
        assert getattr(metric, metric_name) == 0
