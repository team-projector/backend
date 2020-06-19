# -*- coding: utf-8 -*-

import math

from django.db import models
from django.db.models import ExpressionWrapper
from django.db.models.functions import Greatest, Least
from django.utils.timezone import datetime, make_aware, now
from jnt_django_toolbox.consts.time import SECONDS_PER_DAY

from apps.payroll.models import WorkBreak


def paid_work_breaks_days_resolver(
    parent, info, **kwargs,  # noqa:WPS110
) -> int:
    """Returns overall paid work break days for user."""
    user = info.context.user
    if not user.is_authenticated:
        return 0

    current_year = now().year
    lower_boundary = datetime(current_year - 1, 12, 31)  # noqa:WPS432
    upper_boundary = datetime(current_year + 1, 1, 1)  # noqa:WPS432

    total_duration = (
        WorkBreak.objects.filter(
            models.Q(to_date__year=current_year)
            | models.Q(from_date__year=current_year),
            user=user,
            paid=True,
        )
        .annotate(
            duration=ExpressionWrapper(
                Least(make_aware(upper_boundary), models.F("to_date"))
                - Greatest(make_aware(lower_boundary), models.F("from_date")),
                output_field=models.fields.DurationField(),
            ),
        )
        .aggregate(total_duration=models.Sum("duration"))
    )["total_duration"]
    if not total_duration:
        return 0

    return math.ceil(total_duration.total_seconds() / SECONDS_PER_DAY)
