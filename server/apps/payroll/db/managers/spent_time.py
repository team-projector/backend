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
        from apps.development.models.merge_request import STATE_OPENED, STATE_CLOSED, STATE_MERGED

        return self.aggregate(
            total_issues=Coalesce(Sum('time_spent', filter=Q(issues__isnull=False)), 0),
            opened_issues=Coalesce(Sum('time_spent', filter=Q(issues__state=STATE_OPENED)), 0),
            closed_issues=Coalesce(Sum('time_spent', filter=Q(issues__state=STATE_CLOSED)), 0),

            total_merges=Coalesce(Sum('time_spent', filter=Q(mergerequests__isnull=False)), 0),
            opened_merges=Coalesce(Sum('time_spent', filter=Q(mergerequests__state=STATE_OPENED)), 0),
            closed_merges=Coalesce(Sum('time_spent', filter=Q(mergerequests__state=STATE_CLOSED)), 0),
            merged_merges=Coalesce(Sum('time_spent', filter=Q(mergerequests__state=STATE_MERGED)), 0),
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
