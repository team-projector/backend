from django.utils.translation import gettext_lazy as _

from apps.core import injector
from apps.core.utils.apps import BaseAppConfig


class AppConfig(BaseAppConfig):
    """Class represents the "users" application."""

    name = "apps.users"
    verbose_name = _("VN__USERS")

    def ready(self):
        """Trigger on app ready."""
        from apps.users.services.modules import (  # noqa: WPS433
            InfrastructureUserServicesModule,
        )
        from apps.users.logic.modules import (  # noqa: WPS433
            ApplicationUserServicesModule,
        )

        super().ready()

        injector.binder.install(InfrastructureUserServicesModule)
        injector.binder.install(ApplicationUserServicesModule)
