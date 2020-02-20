# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import ExpressionWrapper
from django.db.models.functions import Coalesce, ExtractDay, Greatest, Least
from django.utils.timezone import datetime, make_aware, now

from apps.payroll.models import WorkBreak


def paid_work_breaks_days_resolver(parent, _, **kwargs) -> int:
    """Returns overall paid work break days for user."""
    current_year = now().year
    lower_boundary = datetime(current_year - 1, 12, 31)  # noqa:WPS432
    upper_boundary = datetime(current_year + 1, 1, 1)  # noqa:WPS432

    return WorkBreak.objects.filter(
        models.Q(to_date__year=current_year)
        | models.Q(from_date__year=current_year),
        user=parent["user"],
        paid=True,
    ).annotate(
        duration=ExpressionWrapper(
            Least(make_aware(upper_boundary), models.F("to_date"))
            - Greatest(make_aware(lower_boundary), models.F("from_date")),
            output_field=models.fields.DurationField(),
        ),
        days=ExtractDay("duration"),
    ).aggregate(
        days_sum=Coalesce(
            models.Sum("days"),
            0,
        ),
    )["days_sum"]
