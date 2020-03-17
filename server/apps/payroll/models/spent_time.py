# -*- coding: utf-8 -*-

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.fields import MoneyField
from apps.payroll.models import Payroll
from apps.payroll.models.managers import SpentTimeManager

SECS_IN_HOUR = 60 * 60


class SpentTime(Payroll):  # noqa:WPS230
    """The spent time model."""

    date = models.DateField(null=True)
    customer_sum = MoneyField(
        default=0,
        verbose_name=_("VN__CUSTOMER_SUM"),
        help_text=_("HT__CUSTOMER_SUM"),
    )

    hour_rate = models.FloatField(
        null=True, verbose_name=_("VN__RATE"), help_text=_("HT__RATE"),
    )

    tax_rate = models.FloatField(
        default=0, verbose_name=_("VN__TAX_RATE"), help_text=_("HT__TAX_RATE"),
    )

    customer_rate = models.FloatField(
        null=True,
        verbose_name=_("VN__CUSTOMER_RATE"),
        help_text=_("HT__CUSTOMER_RATE"),
    )

    time_spent = models.IntegerField(
        verbose_name=_("VN__TIME_SPENT"), help_text=_("HT__TIME_SPENT"),
    )

    content_type = models.ForeignKey(ContentType, models.CASCADE)

    object_id = models.PositiveIntegerField()

    base = GenericForeignKey()

    note = models.OneToOneField(
        "development.Note",
        models.SET_NULL,
        null=True,
        blank=True,
        related_name="time_spend",
    )

    objects = SpentTimeManager()  # noqa: WPS110

    class Meta:
        verbose_name = _("VN__SPENT_TIME")
        verbose_name_plural = _("VN__SPENT_TIMES")
        ordering = ("-date",)

    def __str__(self):
        """Returns object string representation."""
        return "{0} [{1}]: {2}".format(self.user, self.base, self.time_spent)

    def save(self, *args, **kwargs) -> None:
        """Save spent time."""
        self.created_by = self.user
        self.hour_rate = self.user.hour_rate  # noqa: WPS601
        self.tax_rate = self.user.tax_rate  # noqa: WPS601
        self.customer_rate = self.user.customer_hour_rate  # noqa: WPS601

        self._adjust_sums()

        super().save(*args, **kwargs)

    def _adjust_sums(self) -> None:
        work_hours = self.time_spent / SECS_IN_HOUR

        self.sum = work_hours * self.hour_rate  # noqa: WPS601
        self.customer_sum = work_hours * self.customer_rate  # noqa: WPS601
