# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _

from apps.core.apps import BaseAppConfig


class AppConfig(BaseAppConfig):
    """Class representing "payroll" application."""

    name = 'apps.payroll'
    verbose_name = _('VN__PAYROLL')
