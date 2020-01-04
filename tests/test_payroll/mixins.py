from datetime import datetime, timedelta
from typing import Dict

from django.test import testcases

from tests.helpers.base import format_date


class CheckUserProgressMetricsMixin(testcases.TestCase):
    def _check_metrics(
        self,
        metrics,
        spents: Dict[datetime, timedelta],
        loadings: Dict[datetime, timedelta],
        issues_counts: Dict[datetime, int],
        time_estimates: Dict[datetime, timedelta],
        time_remains: Dict[datetime, timedelta],
        planned_work_hours: int = 8,
    ):
        spents = self._prepare_metrics(spents)
        loadings = self._prepare_metrics(loadings)
        time_estimates = self._prepare_metrics(time_estimates)
        issues_counts = self._prepare_metrics(issues_counts)
        time_remains = self._prepare_metrics(time_remains)

        for metric in metrics:
            self.assertEqual(metric.get("start"), metric.get("end"))
            self.assertEqual(metric["planned_work_hours"], planned_work_hours)

            self._check_metric(metric, "time_spent", spents)
            self._check_metric(metric, "time_estimate", time_estimates)
            self._check_metric(metric, "loading", loadings)
            self._check_metric(metric, "time_remains", time_remains)

            if metric["start"] in issues_counts:
                self.assertEqual(
                    metric["issues_count"],
                    issues_counts[metric.get("start")],
                )
            else:
                self.assertEqual(metric["issues_count"], 0)

    def _prepare_metrics(self, metrics):
        return {
            format_date(d): time
            for d, time in metrics.items()
        }

    def _check_metric(self, metric, metric_name, values):
        if metric["start"] in values:
            self.assertEqual(
                metric[metric_name],
                values[metric.get("start")].total_seconds(),
                f"bad {metric_name} for {metric['start']}: "
                + f"expected - {values[metric.get('start')]}, "
                + f"actual - {timedelta(seconds=metric[metric_name])}",
            )
        else:
            self.assertEqual(
                metric[metric_name],
                0,
                f"bad {metric_name} for {metric.get('start')}: "
                + "expected - 0, "
                + f"actual - {timedelta(seconds=metric[metric_name])}",
            )
