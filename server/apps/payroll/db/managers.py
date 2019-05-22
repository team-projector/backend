from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Case, F, FloatField, Sum, When
from django.db.models.functions import Coalesce
from django.db.models.manager import BaseManager


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
        return self.annotate(
            payroll=Case(
                When(
                    salary__isnull=True, then=F('sum')
                ),
                default=0,
                output_field=FloatField()
            ),
            paid=Case(
                When(
                    salary__isnull=False, then=F('sum')
                ),
                default=0,
                output_field=FloatField()
            )
        ).aggregate(
            total_payroll=Coalesce(Sum('payroll'), 0),
            total_paid=Coalesce(Sum('paid'), 0)
        )


BaseSpentTimeManager: Any = BaseManager.from_queryset(SpentTimeQuerySet)


class SpentTimeManager(BaseSpentTimeManager):
    pass
