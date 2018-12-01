from django.apps import AppConfig

from .utils.modules import load_module_from_app


class BaseAppConfig(AppConfig):
    def ready(self):
        load_module_from_app(self.name, 'signals.receivers')
