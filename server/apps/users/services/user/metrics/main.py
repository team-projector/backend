from decimal import Decimal
from typing import Dict, List, NamedTuple, Optional, Tuple

from django.db import models
from django.db.models.functions import Coalesce
from jnt_django_toolbox.helpers.dicts import deep_get, deep_set, recursive_dict

from apps.core.models.fields import MoneyField
from apps.development.models.issue import IssueState
from apps.development.models.merge_request import MergeRequestState
from apps.payroll.models import Bonus, Penalty, SpentTime
from apps.users.models import User
from apps.users.services.user.metrics import (
    last_salary_date_resolver,
    paid_work_breaks_days_resolver,
)


class UserMetricsProvider:
    """Merge Request user metrics."""

    def __init__(self, fields: Tuple[str, ...] = ()):
        """Inits object with fields."""
        self._fields = fields
        self._bonus: Optional[Decimal] = None
        self._penalty: Optional[Decimal] = None

    def get_metrics(self, user: User):
        """Calculate and return metrics."""
        metrics = self._get_time_spent_aggregations(user)
        return_metrics = recursive_dict()

        for field, metric in metrics.items():
            deep_set(return_metrics, field, metric)

        if return_metrics.get("taxes", None) is not None:
            bonus = self._get_bonus(user) - self._get_penalty(user)
            return_metrics["taxes"] += bonus * Decimal.from_float(
                user.tax_rate,
            )
            return_metrics["taxes"] = max(
                return_metrics["taxes"],
                Decimal(0),
            ).quantize(
                Decimal("1.00"),
            )

        self._fill_metrics(user, return_metrics)

        return return_metrics

    def _fill_metrics(self, user, metrics) -> None:
        """Fill metrics."""
        metric_request_map = {
            "bonus": self._get_bonus,
            "penalty": self._get_penalty,
            "paid_work_breaks_days": paid_work_breaks_days_resolver,
            "last_salary_date": last_salary_date_resolver,
        }

        for requested_field, func in metric_request_map.items():
            if not self._is_metric_requested(requested_field):
                continue

            metrics[requested_field] = func(user)

    def _get_time_spent_aggregations(self, user: User):
        """
        Get time spent aggregations.

        :param user:
        :type user: User
        """
        ret = SpentTime.objects.filter(
            salary__isnull=True,
            user=user,
        ).aggregate(
            **{
                key: aggr
                for key, aggr in _aggregations().items()
                if self._is_metric_requested(key)
            },
        )

        for metric in ("taxes_opened", "taxes_closed"):
            if ret.get(metric) is None:
                continue

            ret[metric] = Decimal(ret[metric]).quantize(Decimal("1.00"))

        return ret

    def _get_bonus(self, user) -> Decimal:
        """Returns overall not paid bonus sum for user."""
        if self._bonus is not None:
            return self._bonus

        self._bonus = Bonus.objects.filter(
            user=user,
            salary__isnull=True,
        ).aggregate(total=Coalesce(models.Sum("sum"), 0))["total"]
        return self._bonus

    def _get_penalty(self, user) -> Decimal:
        """Returns actual penalties for user."""
        if self._penalty is not None:
            return self._penalty

        self._penalty = Penalty.objects.filter(
            user=user,
            salary__isnull=True,
        ).aggregate(total=Coalesce(models.Sum("sum"), 0))["total"]
        return self._penalty

    def _is_metric_requested(self, metric: str):
        """
        Is metric requested.

        :param metric:
        :type metric: str
        """
        if not self._fields:
            return True

        try:
            deep_get(self._fields, metric)
        except KeyError:
            return False
        else:
            return True


class _Aggregations:
    """Aggregations."""

    issue_opened = models.Q(issues__state=IssueState.OPENED)
    issue_closed = models.Q(issues__state=IssueState.CLOSED)
    mreq_opened = models.Q(mergerequests__state=MergeRequestState.OPENED)
    mreq_closed = models.Q(
        mergerequests__state__in=(
            MergeRequestState.CLOSED,
            MergeRequestState.MERGED,
        ),
    )

    def __call__(self) -> Dict[str, models.Expression]:
        """Call aggregations."""
        ret = {
            "issues.opened_spent": Coalesce(
                models.Sum("time_spent", filter=self.issue_opened),
                0,
            ),
            "issues.closed_spent": Coalesce(
                models.Sum(
                    "time_spent",
                    filter=models.Q(issues__state=IssueState.CLOSED),
                ),
                0,
            ),
            "merge_requests.closed_spent": Coalesce(
                models.Sum(
                    "time_spent",
                    filter=models.Q(
                        mergerequests__state__in=(
                            MergeRequestState.CLOSED,
                            MergeRequestState.MERGED,
                        ),
                    ),
                ),
                0,
            ),
            "merge_requests.opened_spent": Coalesce(
                models.Sum("time_spent", filter=self.mreq_opened),
                0,
            ),
            "opened_spent": Coalesce(
                models.Sum(
                    "time_spent",
                    filter=self.issue_opened | self.mreq_opened,
                ),
                0,
            ),
            "closed_spent": Coalesce(
                models.Sum(
                    "time_spent",
                    filter=models.Q(
                        models.Q(issues__state=IssueState.CLOSED)
                        | models.Q(
                            mergerequests__state__in=(
                                MergeRequestState.CLOSED,
                                MergeRequestState.MERGED,
                            ),
                        ),
                    ),
                ),
                0,
            ),
        }

        aggr_params_list: List[Tuple[str, _WorkItemFilters]] = [
            (
                "issues.",
                _WorkItemFilters(
                    self.issue_opened,
                    self.issue_closed,
                    self.issue_opened | self.issue_closed,
                ),
            ),
            (
                "merge_requests.",
                _WorkItemFilters(
                    self.mreq_opened,
                    self.mreq_closed,
                    self.mreq_opened | self.mreq_closed,
                ),
            ),
            (
                "",
                _WorkItemFilters(
                    self.issue_opened | self.mreq_opened,
                    self.issue_closed | self.mreq_closed,
                    None,
                ),
            ),
        ]

        for aggr_params in aggr_params_list:
            for metric, expr in _work_item_aggrs(aggr_params[1]).items():
                ret["{0}{1}".format(aggr_params[0], metric)] = expr

        return ret


class _WorkItemFilters(NamedTuple):
    opened: models.Q
    closed: models.Q
    all: Optional[models.Q]  # noqa: WPS125


class _WorkItemAggregations:
    """Work item aggregations."""

    tax_rate = models.ExpressionWrapper(
        models.F("tax_rate"),
        output_field=MoneyField(max_length=MoneyField),
    )

    def __call__(
        self,
        filters: _WorkItemFilters,
    ) -> Dict[str, models.Expression]:
        """Call work item aggregations."""
        return {
            "payroll": Coalesce(models.Sum("sum", filter=filters.all), 0),
            "payroll_opened": Coalesce(
                models.Sum("sum", filter=filters.opened),
                0,
            ),
            "payroll_closed": Coalesce(
                models.Sum("sum", filter=filters.closed),
                0,
            ),
            "taxes": Coalesce(
                models.Sum(
                    models.F("sum") * self.tax_rate,
                    filter=filters.all,
                ),
                0,
            ),
            "taxes_opened": Coalesce(
                models.Sum(
                    models.F("sum") * self.tax_rate,
                    filter=filters.opened,
                ),
                0,
            ),
            "taxes_closed": Coalesce(
                models.Sum(
                    models.F("sum") * self.tax_rate,
                    filter=filters.closed,
                ),
                0,
            ),
        }


_aggregations = _Aggregations()
_work_item_aggrs = _WorkItemAggregations()
