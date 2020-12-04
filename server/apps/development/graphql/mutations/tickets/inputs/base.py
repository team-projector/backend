from typing import Dict

from django.core.validators import URLValidator
from jnt_django_graphene_toolbox.serializers.fields.char import CharField
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
            "estimate",
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
    role = CharField(required=False)
    url = CharField(required=False, validators=(URLValidator(),))
    estimate = serializers.IntegerField(
        min_value=0,
        required=False,
        allow_null=True,
    )

    def validate_estimate(self, estimate) -> int:
        """Validate estimate."""
        return estimate or 0

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
