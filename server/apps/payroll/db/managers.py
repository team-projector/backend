from typing import Any

from django.db import models
from django.db.models import Case, F, FloatField, Sum, When
from django.db.models.manager import BaseManager


class SpentTimeQuerySet(models.QuerySet):
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
            total_payroll=Sum('payroll'),
            total_paid=Sum('paid')
        )


BaseSpentTimeManager: Any = BaseManager.from_queryset(SpentTimeQuerySet)


class SpentTimeManager(BaseSpentTimeManager):
    pass
