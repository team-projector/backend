# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.fields import MoneyField
from apps.core.models.mixins import Timestamps


class Payroll(Timestamps):
    """The payroll model."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        verbose_name=_('VN__CREATED_BY'),
        help_text=_('HT__CREATED_BY'),
    )

    sum = MoneyField(  # noqa A003
        default=0,
        verbose_name=_('VN__SUM'),
        help_text=_('HT__SUM'),
    )

    salary = models.ForeignKey(
        'payroll.Salary',
        models.SET_NULL,
        null=True,
        blank=True,
        related_name='payrolls',
        verbose_name=_('VN__SALARY'),
        help_text=_('HT__SALARY'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        related_name='+',
        verbose_name=_('VN__USER'),
        help_text=_('HT__USER'),
    )

    def __str__(self):
        """Returns object string representation."""
        return '{0} [{1}]: {2}'.format(self.user, self.created_at, self.sum)

    class Meta:
        verbose_name = _('VN__PAYROLL')
        verbose_name_plural = _('VN__PAYROLLS')
        ordering = ('-created_at',)
