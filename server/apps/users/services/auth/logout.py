from dataclasses import dataclass

from apps.users.models import Token


@dataclass(frozen=True)
class LogoutInputDto:
    """Logout unput data."""

    token: Token


class LogoutService:
    """Logout service."""

    def execute(self, input_dto: LogoutInputDto) -> None:
        """Main logic."""
        input_dto.token.delete()
