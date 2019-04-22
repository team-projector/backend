from django.db import models
from django.utils.translation import gettext_lazy as _

from .payroll import Payroll


class Bonus(Payroll):
    description = models.TextField(
        verbose_name=_('VN__DESCRIPTION'),
        help_text=_('HT__DESCRIPTION')
    )

    class Meta:
        verbose_name = _('VN__BONUS')
        verbose_name_plural = _('VN__BONUSES')
        ordering = ('-created_at',)
