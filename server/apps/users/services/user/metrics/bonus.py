# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.functions import Coalesce

from apps.payroll.models import Bonus


def bonus_resolver(parent, _, **kwargs) -> float:
    """Returns overall not paid bonus sum for user."""
    return Bonus.objects.filter(
        user=parent["user"],
        salary__isnull=True,
    ).aggregate(
        total_bonus=Coalesce(models.Sum("sum"), 0),
    )["total_bonus"]
