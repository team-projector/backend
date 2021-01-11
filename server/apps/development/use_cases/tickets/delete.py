from dataclasses import dataclass

from rest_framework import serializers

from apps.core.application.errors import AccessDeniedApplicationError
from apps.core.application.use_cases import BasePresenter, BaseUseCase
from apps.development.models import Ticket
from apps.users.models import User


@dataclass(frozen=True)
class TicketDeleteData:
    """Delete ticket data."""

    ticket: int


@dataclass(frozen=True)
class InputDto:
    """Delete ticket input dto."""

    data: TicketDeleteData  # noqa: WPS110
    user: User


class InputDtoSerializer(serializers.Serializer):
    """InputSerializer."""

    ticket = serializers.PrimaryKeyRelatedField(
        queryset=Ticket.objects.all(),
    )


class UseCase(BaseUseCase):
    """Use case for declining tickets."""

    def __init__(self, presenter: BasePresenter):
        """Initialize."""
        self._presenter = presenter

    def execute(self, input_dto: InputDto) -> None:
        """Main logic here."""
        if not input_dto.user.is_project_manager:
            raise AccessDeniedApplicationError()

        validated_data = self.validate_input(
            input_dto.data,
            InputDtoSerializer,
        )
        validated_data["ticket"].delete()
