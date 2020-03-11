# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.functions import Coalesce

from apps.payroll.models import Penalty


def penalty_resolver(parent, _, **kwargs) -> float:
    """Returns actual penalties for user."""
    return Penalty.objects.filter(
        user=parent["user"], salary__isnull=True,
    ).aggregate(total_penalty=Coalesce(models.Sum("sum"), 0))["total_penalty"]
