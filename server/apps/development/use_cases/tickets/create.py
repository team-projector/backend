import dataclasses
import datetime
from dataclasses import dataclass
from typing import List, Optional

from rest_framework import serializers

from apps.core.application.errors import (
    AccessDeniedApplicationError,
    InvalidInputApplicationError,
)
from apps.core.application.use_cases import BaseUseCase
from apps.development.models import Milestone, Ticket, TicketState, TicketType
from apps.development.use_cases.tickets.validators.ticket import (
    BaseTicketValidator,
)
from apps.users.models import User

_MUTABLE_FIELDS = frozenset(
    (
        "title",
        "start_date",
        "due_date",
        "type",
        "state",
        "role",
        "url",
        "estimate",
        "milestone",
    ),
)

_ISSUES_FIELD = "issues"


@dataclass(frozen=True)
class TicketCreateData:
    """Create ticket data."""

    title: str
    start_date: Optional[datetime.date]
    due_date: Optional[datetime.date]
    type: TicketType  # noqa: WPS125
    state: TicketState
    issues: Optional[List[int]]
    role: str
    url: str
    estimate: Optional[str]
    milestone: Optional[int]


@dataclass(frozen=True)
class InputDto:
    """Create ticket input dto."""

    user: User
    data: TicketCreateData  # noqa: TicketCreateData


@dataclass(frozen=True)
class OutputDto:
    """Create ticket output dto."""

    ticket: Ticket


class InputDtoValidator(BaseTicketValidator):
    """InputSerializer."""

    milestone = serializers.PrimaryKeyRelatedField(
        queryset=Milestone.objects,
        allow_null=False,
    )


class UseCase(BaseUseCase[InputDto, OutputDto]):
    """Usecase for updating tickets."""

    def execute(self, input_dto: InputDto) -> OutputDto:
        """Main logic here."""
        if not input_dto.user.is_project_manager:
            raise AccessDeniedApplicationError()

        validator = InputDtoValidator(
            data=dataclasses.asdict(input_dto.data),
            context={"user": input_dto.user},
        )
        if not validator.is_valid():
            raise InvalidInputApplicationError(validator.errors)

        validated_data = validator.validated_data
        ticket = Ticket()

        for field in _MUTABLE_FIELDS:
            setattr(ticket, field, validated_data[field])

        ticket.save()
        ticket.issues.add(*validated_data.get(_ISSUES_FIELD))

        return OutputDto(ticket=ticket)
