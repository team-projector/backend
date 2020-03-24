# -*- coding: utf-8 -*-

from datetime import date, timedelta
from typing import Dict

from tests.helpers.base import format_date


def check_user_progress_metrics(
    metrics,
    spents: Dict[date, timedelta] = None,
    issues_counts: Dict[date, int] = None,
    time_estimates: Dict[date, timedelta] = None,
    efficiencies: Dict[date, float] = None,
):
    spents = _prepare_metrics(spents)
    time_estimates = _prepare_metrics(time_estimates)
    issues_counts = _prepare_metrics(issues_counts)
    efficiencies = _prepare_metrics(efficiencies)

    for metric in metrics:
        assert metric.end == metric.start + timedelta(weeks=1)

        _check_metric(metric, "time_spent", spents)
        _check_metric(metric, "time_estimate", time_estimates)

        start_dt = str(metric.start)
        if start_dt in efficiencies:
            assert efficiencies.get(start_dt) == metric.efficiency
        else:
            assert metric.efficiency == 0

        if start_dt in issues_counts:
            assert issues_counts.get(start_dt) == metric.issues_count
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
