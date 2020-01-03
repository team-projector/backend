# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _

from apps.payroll.models import Payroll


class Payment(Payroll):
    """The payment model."""

    class Meta:
        verbose_name = _("VN__PAYMENT")
        verbose_name_plural = _("VN__PAYMENTS")
        ordering = ("-created_at",)
