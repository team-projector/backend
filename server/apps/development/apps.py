from django.utils.translation import gettext_lazy as _

from apps.core.apps import BaseAppConfig


class AppConfig(BaseAppConfig):
    name = 'apps.development'
    verbose_name = _('VN__DEVELOPMENT')
