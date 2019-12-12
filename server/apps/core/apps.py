# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _

from apps.core.utils.apps import BaseAppConfig
from apps.core.utils.modules import load_module_from_app


class AppConfig(BaseAppConfig):
    """Class representing the "core" application."""

    name = 'apps.core'
    verbose_name = _('VN__CORE')

    def ready(self):
        """Run this code when Django starts."""
        super().ready()

        load_module_from_app(self.name, 'graphql.fields')
