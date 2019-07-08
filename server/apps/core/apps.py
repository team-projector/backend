from django.apps import AppConfig

from apps.core.utils.modules import load_module_from_app


class BaseAppConfig(AppConfig):
    def ready(self):
        load_module_from_app(self.name, 'graphql.types')
