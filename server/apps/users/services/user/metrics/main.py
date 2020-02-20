# -*- coding: utf-8 -*-

from typing import Tuple

from django.db import models
from django.db.models.functions import Coalesce

from apps.core.utils.dicts import deep_get, deep_set, recursive_dict
from apps.development.models.issue import Issue, IssueState
from apps.development.models.merge_request import (
    MergeRequest,
    MergeRequestState,
)
from apps.payroll.models import SpentTime
from apps.users.models import User


class UserMetricsProvider:
    """Merge Request user metrics."""

    def __init__(self, fields: Tuple[str, ...] = ()):
        """Inits object with fields."""
        self._fields = fields

    def get_metrics(self, user: User):
        """Calculate and return metrics."""
        metrics = self._get_time_spent_aggregations(user)
        ret = recursive_dict()
        ret["user"] = user

        for field, metric in metrics.items():
            deep_set(ret, ".".join(field.split("__")), metric)

        if self._is_metric_requested("issues__opened_count"):
            ret["issues"]["opened_count"] = self._get_issues_opened_count(user)

        if self._is_metric_requested("merge_requests__opened_count"):
            ret["merge_requests"]["opened_count"] = self._get_mr_opened_count(user)  # noqa:E501

        return ret

    def _get_issues_opened_count(self, user: User):
        return Issue.objects.filter(
            user=user,
            state=IssueState.OPENED,
        ).count()

    def _get_mr_opened_count(self, user: User):
        return MergeRequest.objects.filter(
            user=user,
            state=MergeRequestState.OPENED,
        ).count()

    def _get_time_spent_aggregations(self, user: User):
        issue_opened = models.Q(issues__state=IssueState.OPENED)
        mr_opend = models.Q(mergerequests__state=MergeRequestState.OPENED)

        aggregations = {
            "payroll": Coalesce(models.Sum("sum"), 0),

            "payroll_opened": Coalesce(
                models.Sum("sum", filter=models.Q(
                    issue_opened
                    | mr_opend,
                )), 0,
            ),

            "payroll_closed": Coalesce(
                models.Sum("sum", filter=models.Q(
                    models.Q(issues__state=IssueState.CLOSED)
                    | models.Q(mergerequests__state__in=(
                        MergeRequestState.CLOSED,
                        MergeRequestState.MERGED,
                    )),
                )), 0,
            ),

            "taxes": Coalesce(models.Sum("tax_sum"), 0),

            "taxes_opened": Coalesce(
                models.Sum("tax_sum", filter=models.Q(issue_opened | mr_opend)),
                0,
            ),

            "taxes_closed": Coalesce(
                models.Sum("tax_sum", filter=models.Q(
                    models.Q(issues__state=IssueState.CLOSED)
                    | models.Q(mergerequests__state__in=(
                        MergeRequestState.CLOSED,
                        MergeRequestState.MERGED,
                    )),
                )), 0,
            ),

            "issues__opened_spent": Coalesce(
                models.Sum("time_spent", filter=issue_opened),
                0,
            ),

            "issues__closed_spent": Coalesce(
                models.Sum(
                    "time_spent",
                    filter=models.Q(issues__state=IssueState.CLOSED),
                ), 0,
            ),

            "merge_requests__closed_spent": Coalesce(
                models.Sum(
                    "time_spent",
                    filter=models.Q(mergerequests__state__in=(
                        MergeRequestState.CLOSED,
                        MergeRequestState.MERGED,
                    )),
                ), 0,
            ),

            "merge_requests__opened_spent": Coalesce(
                models.Sum("time_spent", filter=mr_opend),
                0,
            ),

            "opened_spent": Coalesce(
                models.Sum("time_spent", filter=issue_opened | mr_opend),
                0,
            ),

            "closed_spent": Coalesce(
                models.Sum(
                    "time_spent",
                    filter=models.Q(
                        models.Q(issues__state=IssueState.CLOSED)
                        | models.Q(mergerequests__state__in=(
                            MergeRequestState.CLOSED,
                            MergeRequestState.MERGED,
                        )),
                    ),
                ), 0,
            ),
        }

        return SpentTime.objects.filter(
            salary__isnull=True,
            user=user,
        ).aggregate(**{
            key: aggr
            for key, aggr
            in aggregations.items() if self._is_metric_requested(key)
        })

    def _is_metric_requested(self, metric: str):
        if not self._fields:
            return True

        try:
            deep_get(self._fields, ".".join(metric.split("__")))
        except KeyError:
            return False
        else:
            return True
