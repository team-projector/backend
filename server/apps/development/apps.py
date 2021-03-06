from django.utils.translation import gettext_lazy as _

from apps.core.utils.apps import BaseAppConfig


class AppConfig(BaseAppConfig):
    """Class represents the "development" application."""

    name = "apps.development"
    verbose_name = _("VN__DEVELOPMENT")
