from django.utils.translation import gettext_lazy as _

from apps.core.utils.apps import BaseAppConfig


class AppConfig(BaseAppConfig):
    """Class representing the "users" application."""

    name = "apps.users"
    verbose_name = _("VN__USERS")
