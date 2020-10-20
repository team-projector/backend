from django.utils.translation import gettext_lazy as _

from apps.core.utils.apps import BaseAppConfig


class AppConfig(BaseAppConfig):
    """Class represents the "skills" application."""

    name = "apps.skills"
    verbose_name = _("VN__SKILLS")
