# -*- coding: utf-8 -*-

from typing import Dict

from rest_framework import serializers
from rest_framework.fields import Field

from apps.core.drf.fields.choices_field import ChoicesField
from apps.development.models import Issue
from apps.development.models.ticket import Ticket, TicketState, TicketType
from apps.development.services.issue.allowed import filter_allowed_for_user


class TicketBaseInput(serializers.ModelSerializer):
    """Ticket base serializer."""

    class Meta:
        model = Ticket
        fields = [
            "type",
            "title",
            "start_date",
            "due_date",
            "url",
            "issues",
            "role",
            "state",
            "milestone",
        ]

    # we should redefine this field because django-graphene has a bug with a
    # choice fields. It creates enums types for these which leads to an error:
    # "AssertionError: Found different types with the same name in the schema:
    # type, type."
    type = ChoicesField(  # noqa: WPS125, A003
        required=False,
        choices=TicketType.values,
    )

    state = ChoicesField(choices=TicketState.values, required=False)

    issues = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        write_only=True,
        queryset=Issue.objects,
    )

    def get_fields(self) -> Dict[str, Field]:
        """Returns serializer fields."""
        fields = super().get_fields()

        if self.context:
            issues_qs = filter_allowed_for_user(
                Issue.objects.all(),
                self.context["request"].user,
            )
            fields["issues"].child_relation.queryset = issues_qs

        return fields
