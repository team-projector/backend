# -*- coding: utf-8 -*-

from typing import Dict

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import Field

from apps.development.graphql.mutations.inputs import TicketBaseInput
from apps.development.models import Issue
from apps.development.models.ticket import Ticket

ISSUES_PARAM_ERROR = 'Please, choose one parameter: "attachIssues" or "issues"'


class TicketUpdateInput(TicketBaseInput):
    """Ticket update serializer."""

    attach_issues = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        write_only=True,
        queryset=Issue.objects,
    )

    id = serializers.PrimaryKeyRelatedField(  # noqa:A003
        queryset=Ticket.objects.all(),
    )

    class Meta(TicketBaseInput.Meta):
        fields = ['id', *TicketBaseInput.Meta.fields, 'attach_issues']

    def get_fields(self) -> Dict[str, Field]:
        """Returns serializer fields."""
        fields = super().get_fields()

        for field in fields.values():
            field.required = False

        if self.context:
            issues_qs = Issue.objects.allowed_for_user(
                self.context['request'].user,
            )
            fields['attach_issues'].child_relation.queryset = issues_qs

        return fields

    def validate(self, attrs):
        """Validates input parameters."""
        if attrs.get('issues') and attrs.get('attach_issues'):
            raise ValidationError(ISSUES_PARAM_ERROR)

        return attrs

    @property
    def validated_data(self):
        """Validated data changing."""
        ret = super().validated_data
        ret['ticket'] = ret.pop('id', None)
        return ret
