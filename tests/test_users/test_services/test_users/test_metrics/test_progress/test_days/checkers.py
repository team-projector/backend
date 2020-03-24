# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from typing import Dict

from apps.users.services.user.metrics import UserProgressMetricsList
from tests.helpers.base import format_date


def check_user_progress_metrics(
    metrics: UserProgressMetricsList,
    spents: Dict[date, timedelta] = None,
    loadings: Dict[date, timedelta] = None,
    issues_counts: Dict[datetime, int] = None,
    time_estimates: Dict[datetime, timedelta] = None,
    time_remains: Dict[datetime, timedelta] = None,
    planned_work_hours: int = 8,
):
    """Check user progress metrics."""
    spents = _prepare_metrics(spents)
    loadings = _prepare_metrics(loadings)
    time_estimates = _prepare_metrics(time_estimates)
    time_remains = _prepare_metrics(time_remains)
    issues_counts = _prepare_metrics(issues_counts)

    for metric in metrics:
        assert metric.start == metric.end
        assert metric.planned_work_hours == planned_work_hours

        _check_timedelta_metric(metric, "time_spent", spents)
        _check_timedelta_metric(metric, "time_estimate", time_estimates)
        _check_timedelta_metric(metric, "loading", loadings)
        _check_timedelta_metric(metric, "time_remains", time_remains)
        _check_number_metric(metric, "issues_count", issues_counts)


def check_user_progress_payroll_metrics(
    metrics: UserProgressMetricsList,
    payroll: Dict[date, float] = None,
    paid: Dict[date, float] = None,
    planned_work_hours: int = 8,
):
    """Check user progress payroll metrics."""
    payroll = _prepare_metrics(payroll)
    paid = _prepare_metrics(paid)

    for metric in metrics:
        assert metric.start == metric.end
        assert metric.planned_work_hours == planned_work_hours

        _check_number_metric(metric, "payroll", payroll)
        _check_number_metric(metric, "paid", paid)


def _prepare_metrics(metrics):
    if metrics is None:
        return {}

    return {
        format_date(metric_date): time for metric_date, time in metrics.items()
    }


def _check_timedelta_metric(metric, metric_name, values):
    dt = str(metric.start)

    if dt in values:
        assert getattr(metric, metric_name) == values.get(dt).total_seconds()
    else:
        assert getattr(metric, metric_name) == 0


def _check_number_metric(metric, metric_name, values):
    dt = str(metric.start)

    if dt in values:
        assert getattr(metric, metric_name) == values.get(dt)
    else:
        assert getattr(metric, metric_name) == 0
