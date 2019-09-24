# -*- coding: utf-8 -*-

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.fields import MoneyField
from apps.payroll.models.managers import SpentTimeManager
from .payroll import Payroll

SECS_IN_HOUR = 60 * 60


class SpentTime(Payroll):
    date = models.DateField(
        null=True,
    )

    customer_sum = MoneyField(
        default=0,
        verbose_name=_('VN__CUSTOMER_SUM'),
        help_text=_('HT__CUSTOMER_SUM'),
    )

    rate = models.FloatField(
        null=True,
        verbose_name=_('VN__RATE'),
        help_text=_('HT__RATE'),
    )

    customer_rate = models.FloatField(
        null=True,
        verbose_name=_('VN__CUSTOMER_RATE'),
        help_text=_('HT__CUSTOMER_RATE'),
    )

    time_spent = models.IntegerField(
        verbose_name=_('VN__TIME_SPENT'),
        help_text=_('HT__TIME_SPENT'),
    )

    content_type = models.ForeignKey(
        ContentType,
        models.CASCADE,
    )

    object_id = models.PositiveIntegerField()

    base = GenericForeignKey()

    note = models.OneToOneField(
        'development.Note',
        models.SET_NULL,
        null=True,
        blank=True,
        related_name='time_spend',
    )

    objects = SpentTimeManager()

    def __str__(self):
        return f'{self.user} [{self.base}]: {self.time_spent}'

    def save(self, *args, **kwargs):
        self.created_by = self.user
        self.rate = self.user.hour_rate
        self.customer_rate = self.user.customer_hour_rate

        self._adjust_sums()

        super().save(*args, **kwargs)

    def _adjust_sums(self):
        self.sum = self.time_spent / SECS_IN_HOUR * self.rate
        self.customer_sum = self.time_spent / SECS_IN_HOUR * self.customer_rate

    class Meta:
        verbose_name = _('VN__SPENT_TIME')
        verbose_name_plural = _('VN__SPENT_TIMES')
        ordering = ('-date',)
