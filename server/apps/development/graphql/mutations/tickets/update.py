from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo
from jnt_django_graphene_toolbox.mutations import SerializerMutation
from rest_framework import exceptions, serializers
from rest_framework.fields import Field

from apps.core.graphql.helpers.persisters import update_from_validated_data
from apps.core.graphql.security.permissions import AllowProjectManager
from apps.development.graphql.mutations.tickets.inputs.base import (
    TicketBaseInput,
)
from apps.development.graphql.types import TicketType
from apps.development.models import Issue, Ticket
from apps.development.services.issue.allowed import filter_allowed_for_user

ISSUES_PARAM_ERROR = 'Please, choose one parameter: "attachIssues" or "issues"'
KEY_ATTACH_ISSUES = "attach_issues"


class InputSerializer(TicketBaseInput):
    """InputSerializer."""

    class Meta(TicketBaseInput.Meta):
        fields = ["id", *TicketBaseInput.Meta.fields, KEY_ATTACH_ISSUES]

    attach_issues = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        write_only=True,
        queryset=Issue.objects,
    )

    id = serializers.PrimaryKeyRelatedField(  # noqa:WPS125, A003
        queryset=Ticket.objects.all(),
    )

    @property
    def validated_data(self):
        """Validated data changing."""
        validated_data = super().validated_data
        validated_data["ticket"] = validated_data.pop("id", None)
        return validated_data

    def get_fields(self) -> Dict[str, Field]:
        """Returns serializer fields."""
        fields = super().get_fields()

        for field in fields.values():
            field.required = False

        if self.context:
            issues_qs = filter_allowed_for_user(
                Issue.objects.all(),
                self.context["request"].user,
            )
            fields[KEY_ATTACH_ISSUES].child_relation.queryset = issues_qs

        return fields

    def validate(self, attrs):
        """Validates input parameters."""
        if attrs.get("issues") and attrs.get(KEY_ATTACH_ISSUES):
            raise exceptions.ValidationError(ISSUES_PARAM_ERROR)

        return attrs


class UpdateTicketMutation(SerializerMutation):
    """Update ticket mutation."""

    class Meta:
        serializer_class = InputSerializer

    ticket = graphene.Field(TicketType)
    permission_classes = (AllowProjectManager,)

    @classmethod
    def perform_mutate(  # type: ignore
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110ø
        validated_data: Dict[str, Any],
    ) -> "UpdateTicketMutation":
        """Overrideable mutation operation."""
        ticket = validated_data.pop("ticket")
        attach_issues = validated_data.pop(KEY_ATTACH_ISSUES, None)
        issues = validated_data.pop("issues", None)

        update_from_validated_data(ticket, validated_data)

        if attach_issues:
            ticket.issues.add(*attach_issues)

        if issues is not None:
            Issue.objects.filter(ticket=ticket).exclude(
                id__in=[issue.pk for issue in issues],
            ).update(ticket=None)

            ticket.issues.add(*issues)

        return cls(ticket=ticket)
