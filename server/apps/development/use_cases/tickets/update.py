import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional

from django.core.validators import URLValidator
from jnt_django_graphene_toolbox.serializers.fields.char import CharField
from rest_framework import serializers

from apps.core.application.use_cases import BasePresenter, BaseUseCase
from apps.core.consts import DEFAULT_TITLE_LENGTH
from apps.core.drf.fields.choices_field import ChoicesField
from apps.development import services
from apps.development.models import (
    TICKET_ROLE_MAX_LENGTH,
    Issue,
    Milestone,
    Ticket,
    TicketState,
    TicketType,
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


class InputDtoSerializer(serializers.ModelSerializer):
    """InputSerializer."""

    class Meta:
        model = Ticket
        fields = "__all__"

    ticket = serializers.PrimaryKeyRelatedField(queryset=Ticket.objects.all())
    title = CharField(max_length=DEFAULT_TITLE_LENGTH)
    start_date = serializers.DateField(allow_null=True)
    due_date = serializers.DateField(allow_null=True)
    type = ChoicesField(  # noqa: WPS125, A003
        choices=TicketType.values,
        allow_blank=True,
    )
    state = ChoicesField(
        choices=TicketState.values,
        allow_blank=True,
    )
    issues = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Issue.objects,
        allow_null=True,
    )
    attach_issues = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Issue.objects,
        allow_null=True,
    )
    role = CharField(max_length=TICKET_ROLE_MAX_LENGTH)
    url = CharField(validators=(URLValidator(),))
    estimate = serializers.IntegerField(min_value=0)
    milestone = serializers.PrimaryKeyRelatedField(
        queryset=Milestone.objects,
        allow_null=True,
    )

    def get_fields(self) -> Dict[str, serializers.Field]:
        """Returns serializer fields."""
        fields = super().get_fields()

        for field in fields.values():
            field.required = False

        if not self.context:
            return fields

        issues_qs = services.issue.allowed.filter_allowed_for_user(
            Issue.objects.all(),
            self.context["request"].user,
        )
        fields["attach_issues"].child_relation.queryset = issues_qs
        fields[_ISSUES_FIELD].child_relation.queryset = issues_qs

        fields[
            "milestone"
        ].queryset = services.mileston.allowed.filter_allowed_for_user(
            Milestone.objects.all(),
            self.context["request"].user,
        )

        return fields

    def validate(self, attrs):
        """Validates input parameters."""
        if attrs.get(_ISSUES_FIELD) and attrs.get("attach_issues"):
            raise serializers.ValidationError(ISSUES_PARAM_ERROR)

        return attrs


class UseCase(BaseUseCase):
    """Usecase for updating tickets."""

    def __init__(self, presenter: BasePresenter):
        """Initialize."""
        self._presenter = presenter

    def execute(self, input_dto: InputDto) -> None:
        """Main logic here."""
        validated_data = self.validate_input(
            input_dto.data,
            InputDtoSerializer,
        )

        ticket = validated_data.pop("ticket")
        attach_issues = validated_data.pop("attach_issues", None)
        issues = validated_data.pop(_ISSUES_FIELD, None)

        if attach_issues:
            ticket.issues.add(*attach_issues)

        if _ISSUES_FIELD in input_dto.fields_to_update:
            Issue.objects.filter(ticket=ticket).exclude(
                id__in=[issue.pk for issue in issues],
            ).update(ticket=None)

            ticket.issues.add(*issues)

        for field in _MUTABLE_FIELDS:
            if field not in input_dto.fields_to_update:
                continue
            setattr(ticket, field, validated_data[field])

        ticket.save()
        self._presenter.present(OutputDto(ticket=ticket))
