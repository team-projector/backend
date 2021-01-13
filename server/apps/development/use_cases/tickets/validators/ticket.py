from typing import Dict

from django.core.validators import URLValidator
from jnt_django_toolbox.helpers import dicts
from rest_framework import serializers

from apps.core.consts import DEFAULT_TITLE_LENGTH
from apps.core.drf.fields.choices_field import ChoicesField
from apps.development.models import (
    TICKET_ROLE_MAX_LENGTH,
    Issue,
    TicketState,
    TicketType,
)
from apps.development.services.issue.allowed import filter_allowed_for_user


class BaseTicketValidator(serializers.Serializer):
    """BaseTicketValidator."""

    title = serializers.CharField(max_length=DEFAULT_TITLE_LENGTH)
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
    role = serializers.CharField(
        max_length=TICKET_ROLE_MAX_LENGTH,
        allow_null=True,
        allow_blank=True,
    )
    url = serializers.CharField(
        validators=(URLValidator(),),
        allow_null=True,
        allow_blank=True,
    )
    estimate = serializers.IntegerField(min_value=0)

    def get_fields(self) -> Dict[str, serializers.Field]:
        """Returns serializer fields."""
        fields = super().get_fields()

        if not self.context:
            return fields

        issues_qs = filter_allowed_for_user(
            Issue.objects.all(),
            self.context["user"],
        )
        fields["issues"].child_relation.queryset = issues_qs

        return fields

    def to_internal_value(self, validated_data):
        """Returns python dict."""
        value_data = super().to_internal_value(validated_data)
        dicts.set_value_if_none(value_data, "role", "")
        dicts.set_value_if_none(value_data, "url", "")

        return value_data
