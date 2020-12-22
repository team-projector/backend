import injector

from apps.users.application.interfaces import ITokenService
from apps.users.services.token import TokenService


class UserServicesModule(injector.Module):
    """Setup di for user services."""

    def configure(self, binder: injector.Binder) -> None:
        """Bind services."""
        binder.bind(ITokenService, to=TokenService, scope=injector.singleton)
