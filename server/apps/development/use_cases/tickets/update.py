import datetime
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.core.application.errors import (
    AccessDeniedApplicationError,
    InvalidInputApplicationError,
)
from apps.core.application.use_cases import BaseUseCase
from apps.core.utils import dataclasses
from apps.development.models import (
    Issue,
    Milestone,
    Ticket,
    TicketState,
    TicketType,
)
from apps.development.tasks import add_issue_note_task
from apps.development.use_cases.tickets.validators.ticket import (
    BaseTicketValidator,
)
from apps.users.models import User

ISSUES_PARAM_ERROR = 'Please, choose one parameter: "attachIssues" or "issues"'
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
class TicketUpdateData:
    """Update ticket data."""

    ticket: int
    title: str
    start_date: Optional[datetime.date]
    due_date: Optional[datetime.date]
    type: TicketType  # noqa: WPS125
    state: TicketState
    issues: Optional[List[int]]
    attach_issues: Optional[List[int]]
    role: str
    url: str
    estimate: Optional[str]
    milestone: Optional[int]


@dataclass(frozen=True)
class InputDto:
    """Update ticket input dto."""

    user: User
    data: TicketUpdateData  # noqa: TicketUpdateData
    fields_to_update: List[str]


@dataclass(frozen=True)
class OutputDto:
    """Update ticket output dto."""

    ticket: Ticket


class InputDtoValidator(BaseTicketValidator):
    """InputSerializer."""

    ticket = serializers.PrimaryKeyRelatedField(queryset=Ticket.objects.all())
    attach_issues = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Issue.objects,
        allow_null=True,
    )
    milestone = serializers.PrimaryKeyRelatedField(
        queryset=Milestone.objects,
        allow_null=True,
    )

    def get_fields(self) -> Dict[str, serializers.Field]:
        """Returns serializer fields."""
        fields = super().get_fields()

        issues_queryset = fields["issues"].child_relation.queryset
        fields["attach_issues"].child_relation.queryset = issues_queryset
        return fields

    def validate(self, attrs):
        """Validates input parameters."""
        if attrs.get(_ISSUES_FIELD) and attrs.get("attach_issues"):
            raise serializers.ValidationError(ISSUES_PARAM_ERROR)

        return attrs


class UseCase(BaseUseCase[InputDto, OutputDto]):
    """Usecase for updating tickets."""

    def execute(self, input_dto: InputDto) -> OutputDto:
        """Main logic here."""
        if not input_dto.user.is_project_manager:
            raise AccessDeniedApplicationError()

        validator = InputDtoValidator(
            data=dataclasses.to_dict(
                input_dto.data,
                input_dto.fields_to_update,
            ),
            context={"user": input_dto.user},
            partial=True,
        )
        if not validator.is_valid():
            raise InvalidInputApplicationError(validator.errors)

        validated_data = validator.validated_data

        ticket = validated_data.pop("ticket")

        for field in _MUTABLE_FIELDS:
            if field not in input_dto.fields_to_update:
                continue
            setattr(ticket, field, validated_data[field])

        ticket.save()

        attach_issues = validated_data.get("attach_issues")

        self._handle_issues(
            ticket=ticket,
            issues=validated_data.get(_ISSUES_FIELD),
            attach_issues=attach_issues,
            input_dto=input_dto,
        )
        self._add_issue_note(
            input_dto.user,
            attach_issues,
            ticket,
        )
        return OutputDto(ticket=ticket)

    def _handle_issues(
        self,
        ticket: Ticket,
        issues: Iterable[Issue],
        attach_issues: Iterable[Issue],
        input_dto: InputDto,
    ):
        if attach_issues:
            ticket.issues.add(*attach_issues)

        if _ISSUES_FIELD in input_dto.fields_to_update:
            Issue.objects.filter(ticket=ticket).exclude(
                id__in=[issue.pk for issue in issues],
            ).update(ticket=None)

            ticket.issues.add(*issues)

    def _add_issue_note(self, user, issues, ticket) -> None:
        """Generate tasks for create issue notes."""
        if not issues or not user.gl_token:
            return

        note_message = _("MSG__ISSUE_WAS_ATTACHED_TO_TICKET {ticket}").format(
            ticket="[{0}]({1})".format(ticket.title.title(), ticket.site_url),
        )

        for issue in issues:
            add_issue_note_task.delay(
                user_id=user.pk,
                issue_id=issue.pk,
                message=note_message,
            )
