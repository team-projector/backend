from django.utils.translation import gettext_lazy as _

from apps.core.utils.apps import BaseAppConfig


class AppConfig(BaseAppConfig):
    """Class represents "payroll" application."""

    name = "apps.payroll"
    verbose_name = _("VN__PAYROLL")
