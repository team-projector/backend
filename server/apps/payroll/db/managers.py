from typing import Any

from django.db import models
from django.db.models import Case, F, FloatField, Q, Sum, When
from django.db.models.manager import BaseManager


class SpentTimeQuerySet(models.QuerySet):
    def aggregate_payrolls(self):
        from apps.development.models import STATE_CLOSED, STATE_OPENED

        return self.annotate(
            payroll_opened=Case(
                When(Q(salary__isnull=True) & Q(issues__state=STATE_OPENED), then=F('sum')),
                default=0,
                output_field=FloatField()),
            payroll_closed=Case(
                When(Q(salary__isnull=True) & Q(issues__state=STATE_CLOSED), then=F('sum')),
                default=0,
                output_field=FloatField()),
            paid=Case(
                When(salary__isnull=False, then=F('sum')),
                default=0,
                output_field=FloatField())) \
            .aggregate(total_payroll_opened=Sum('payroll_opened'),
                       total_payroll_closed=Sum('payroll_closed'),
                       total_paid=Sum('paid'))


BaseSpentTimeManager: Any = BaseManager.from_queryset(SpentTimeQuerySet)


class SpentTimeManager(BaseSpentTimeManager):
    pass
