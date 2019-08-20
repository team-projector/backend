from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Case, F, FloatField, QuerySet, Sum, When, Q
from django.db.models.functions import Coalesce
from django.db.models.manager import BaseManager

from apps.payroll.services.allowed.spent_time import filter_allowed_for_user


class SpentTimeQuerySet(models.QuerySet):
    def for_issues(self, issues):
        from apps.development.models import Issue

        ct = ContentType.objects.get_for_model(Issue)
        queryset = self.filter(
            content_type=ct,
            object_id__in=issues.values_list('id')
        )

        return queryset

    def aggregate_payrolls(self):
        return self.annotate_payrolls().aggregate(
            total_payroll=Coalesce(Sum('payroll'), 0),
            total_paid=Coalesce(Sum('paid'), 0)
        )

    def summaries(self):
        from apps.development.models import merge_request
        from apps.development.models import issue

        def _h(**filters) -> Coalesce:
            return Coalesce(Sum('time_spent', filter=Q(**filters)), 0)

        return self.aggregate(
            total_issues=_h(issues__isnull=False),
            opened_issues=_h(issues__state=issue.STATE_OPENED),
            closed_issues=_h(issues__state=issue.STATE_CLOSED),

            total_merges=_h(mergerequests__isnull=False),
            opened_merges=_h(mergerequests__state=merge_request.STATE_OPENED),
            closed_merges=_h(mergerequests__state=merge_request.STATE_CLOSED),
            merged_merges=_h(mergerequests__state=merge_request.STATE_MERGED),
        )

    def annotate_payrolls(self,
                          paid: bool = True,
                          payroll: bool = True) -> QuerySet:
        queryset = self

        if paid:
            queryset = queryset.annotate(
                paid=Case(
                    When(
                        salary__isnull=False, then=F('sum')
                    ),
                    default=0,
                    output_field=FloatField()
                )
            )

        if payroll:
            queryset = queryset.annotate(
                payroll=Case(
                    When(
                        salary__isnull=True, then=F('sum')
                    ),
                    default=0,
                    output_field=FloatField()
                ),
            )

        return queryset


BaseSpentTimeManager: Any = BaseManager.from_queryset(SpentTimeQuerySet)


class SpentTimeManager(BaseSpentTimeManager):
    def allowed_for_user(self, user):
        return filter_allowed_for_user(self, user)
