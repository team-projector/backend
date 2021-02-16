import injector

from apps.users.services.auth.login import LoginService
from apps.users.services.auth.logout import LogoutService
from apps.users.services.auth.social_login import SocialLoginService
from apps.users.services.token import TokenService


class InfrastructureUserServicesModule(injector.Module):
    """Setup di for user services."""

    def configure(self, binder: injector.Binder) -> None:
        """Bind services."""
        binder.bind(TokenService, scope=injector.singleton)
        binder.bind(LoginService, scope=injector.singleton)
        binder.bind(LogoutService, scope=injector.singleton)
        binder.bind(SocialLoginService, scope=injector.singleton)
