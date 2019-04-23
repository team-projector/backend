from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.fields import MoneyField
from apps.core.db.mixins import Timestamps

User = get_user_model()


class Salary(Timestamps):
    created_by = models.ForeignKey(
        User,
        models.CASCADE,
        verbose_name=_('VN__CREATED_BY'),
        help_text=_('HT__CREATED_BY')
    )

    user = models.ForeignKey(
        User,
        models.CASCADE,
        related_name='salaries',
        verbose_name=_('VN__USER'),
        help_text=_('HT__USER')
    )

    period_from = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('VN__PERIOD_FROM'),
        help_text=_('HT__PERIOD_FROM')
    )

    period_to = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('VN__PERIOD_TO'),
        help_text=_('HT__PERIOD_TO')
    )

    charged_time = models.IntegerField(
        default=0,
        verbose_name=_('VN__CHARGED_TIME'),
        help_text=_('HT__CHARGED_TIME')
    )

    taxes = MoneyField(
        default=0,
        verbose_name=_('VN__TAXES'),
        help_text=_('HT__TAXES')
    )

    bonus = MoneyField(
        default=0,
        verbose_name=_('VN__BONUS'),
        help_text=_('HT__BONUS')
    )

    penalty = MoneyField(
        default=0,
        verbose_name=_('VN__PENALTY'),
        help_text=_('HT__PENALTY')
    )

    sum = MoneyField(
        default=0,
        verbose_name=_('VN__SUM'),
        help_text=_('HT__SUM')
    )

    total = MoneyField(
        default=0,
        verbose_name=_('VN__TOTAL'),
        help_text=_('HT__TOTAL')
    )

    payed = models.BooleanField(
        default=False,
        verbose_name=_('VN__PAYED'),
        help_text=_('HT__PAYED')
    )

    comments = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('VN__COMMENTS'),
        help_text=_('HT__COMMENTS')
    )

    def __str__(self):
        return f'{self.user} [{self.created_at}]: {self.sum}'

    class Meta:
        verbose_name = _('VN__SALARY')
        verbose_name_plural = _('VN__SALARIES')
        ordering = ('-created_at',)
