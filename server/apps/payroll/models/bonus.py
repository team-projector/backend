# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.payroll.models.payroll import Payroll


class Bonus(Payroll):
    """The bonus model."""

    description = models.TextField(
        verbose_name=_('VN__DESCRIPTION'),
        help_text=_('HT__DESCRIPTION'),
    )

    class Meta:
        verbose_name = _('VN__BONUS')
        verbose_name_plural = _('VN__BONUSES')
        ordering = ('-created_at',)
