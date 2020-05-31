# -*- coding: utf-8 -*-

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _


class SpentTimesMixin(models.Model):
    """Spent time mixin."""

    class Meta:
        abstract = True

    time_spents = GenericRelation(
        "payroll.SpentTime",
        related_query_name="%(class)ss",
        verbose_name=_("VN__TIME_SPENTS"),
        help_text=_("HT__TIME_SPENTS"),
    )

    def __str__(self):
        """Returns object string representation."""
        return ""
