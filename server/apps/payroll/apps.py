from django.utils.translation import gettext_lazy as _

from apps.core.apps import BaseAppConfig


class AppConfig(BaseAppConfig):
    name = 'apps.payroll'
    verbose_name = _('VN__PAYROLL')

    def ready(self):
        import apps.payroll.signal_handlers # noqa
