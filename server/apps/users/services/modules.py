import injector

from apps.users.services.login import LoginService
from apps.users.services.token import TokenService


class UserServicesModule(injector.Module):
    """Setup di for user services."""

    def configure(self, binder: injector.Binder) -> None:
        """Bind services."""
        binder.bind(TokenService, scope=injector.singleton)
        binder.bind(LoginService, scope=injector.singleton)
