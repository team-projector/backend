# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.payroll.models import Payroll


class Penalty(Payroll):
    """The penalty model."""

    comment = models.TextField(
        verbose_name=_("VN__COMMENT"),
        help_text=_("HT__COMMENT"),
    )

    class Meta:
        verbose_name = _("VN__PENALTY")
        verbose_name_plural = _("VN__PENALTIES")
        ordering = ("-created_at",)
