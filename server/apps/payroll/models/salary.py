# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import FieldTracker

from apps.core.models.fields import MoneyField
from apps.core.models.mixins import Timestamps
from apps.core.models.validators import tax_rate_validator
from apps.payroll.models.managers import SalaryManager
from apps.users.models import Position


class Salary(Timestamps):
    """The salary model."""

    class Meta:
        verbose_name = _("VN__SALARY")
        verbose_name_plural = _("VN__SALARIES")
        ordering = ("-created_at",)

    period_from = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("VN__PERIOD_FROM"),
        help_text=_("HT__PERIOD_FROM"),
    )

    period_to = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("VN__PERIOD_TO"),
        help_text=_("HT__PERIOD_TO"),
    )

    charged_time = models.IntegerField(
        default=0,
        verbose_name=_("VN__CHARGED_TIME"),
        help_text=_("HT__CHARGED_TIME"),
    )

    hour_rate = models.FloatField(
        default=0,
        verbose_name=_("VN__HOUR_RATE"),
        help_text=_("HT__HOUR_RATE"),
    )

    tax_rate = models.FloatField(
        default=0,
        verbose_name=_("VN__TAX_RATE"),
        help_text=_("HT__TAX_RATE"),
        validators=(tax_rate_validator,),
    )

    taxes = MoneyField(
        default=0, verbose_name=_("VN__TAXES"), help_text=_("HT__TAXES"),
    )

    bonus = MoneyField(
        default=0, verbose_name=_("VN__BONUS"), help_text=_("HT__BONUS"),
    )

    penalty = MoneyField(
        default=0, verbose_name=_("VN__PENALTY"), help_text=_("HT__PENALTY"),
    )

    sum = MoneyField(  # noqa: WPS125, A003
        default=0, verbose_name=_("VN__SUM"), help_text=_("HT__SUM"),
    )

    total = MoneyField(
        default=0, verbose_name=_("VN__TOTAL"), help_text=_("HT__TOTAL"),
    )

    payed = models.BooleanField(
        default=False, verbose_name=_("VN__PAYED"), help_text=_("HT__PAYED"),
    )

    comment = models.TextField(
        blank=True, verbose_name=_("VN__COMMENT"), help_text=_("HT__COMMENT"),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        verbose_name=_("VN__CREATED_BY"),
        help_text=_("HT__CREATED_BY"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        related_name="salaries",
        verbose_name=_("VN__USER"),
        help_text=_("HT__USER"),
    )

    position = models.ForeignKey(  # noqa: CCE001
        Position,
        models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("VN__POSITION"),
        help_text=_("HT__POSITION"),
    )

    objects = SalaryManager()  # noqa: WPS110

    field_tracker = FieldTracker()

    def __str__(self):
        """Returns object string representation."""
        return "{0} [{1}]: {2}".format(self.user, self.created_at, self.sum)
