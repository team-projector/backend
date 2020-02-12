# -*- coding: utf-8 -*-

from typing import Dict

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import Field

from apps.development.models import Issue
from apps.development.models.ticket import (
    TICKET_STATE_MAX_LENGTH,
    TICKET_STATES,
    TICKET_TYPE_MAX_LENGTH,
    TICKET_TYPES,
    Ticket,
)


class TicketBaseInput(serializers.ModelSerializer):
    """Ticket base serializer."""

    # we should redefine this field because django-graphene has a bug with a
    # choice fields. It creates enums types for these which leads to an error:
    # "AssertionError: Found different types with the same name in the schema:
    # type, type."
    type = serializers.CharField(  # noqa: A003
        required=False,
        max_length=TICKET_TYPE_MAX_LENGTH,
    )

    state = serializers.CharField(
        max_length=TICKET_STATE_MAX_LENGTH,
    )

    issues = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        write_only=True,
        queryset=Issue.objects,
    )

    class Meta:
        model = Ticket
        fields = [
            "type", "title", "start_date", "due_date", "url", "issues", "role",
            "state",
        ]

    def get_fields(self) -> Dict[str, Field]:
        """Returns serializer fields."""
        fields = super().get_fields()

        if self.context:
            issues_qs = Issue.objects.allowed_for_user(
                self.context["request"].user,
            )
            fields["issues"].child_relation.queryset = issues_qs

        return fields

    def validate_type(self, type_):
        """Validates type is one of the valid choices."""
        if type_ and type_ not in TICKET_TYPES.keys():
            raise ValidationError(
                "type should be one of available choices: {0}".format(
                    ", ".join(TICKET_TYPES.keys()),
                ),
            )

        return type_

    def validate_state(self, state):
        """Validates state is one of the valid choices."""
        if state and state not in TICKET_STATES.keys():
            raise ValidationError(
                "state should be one of available choices: {0}".format(
                    ", ".join(TICKET_STATES.keys()),
                ),
            )

        return state
