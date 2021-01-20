from dataclasses import dataclass

from rest_framework import serializers

from apps.core.application.errors import AccessDeniedApplicationError
from apps.core.application.use_cases import BaseUseCase
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


@dataclass(frozen=True)
class OutputDto:
    """Delete ticket output dto."""


class InputDtoValidator(serializers.Serializer):
    """InputSerializer."""

    ticket = serializers.PrimaryKeyRelatedField(
        queryset=Ticket.objects.all(),
    )


class UseCase(BaseUseCase[InputDto, OutputDto]):
    """Use case for declining tickets."""

    def execute(self, input_dto: InputDto) -> OutputDto:
        """Main logic here."""
        if not input_dto.user.is_project_manager:
            raise AccessDeniedApplicationError()

        validated_data = self.validate_input(input_dto.data, InputDtoValidator)
        validated_data["ticket"].delete()

        return OutputDto()
