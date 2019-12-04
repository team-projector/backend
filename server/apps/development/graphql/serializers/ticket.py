# -*- coding: utf-8 -*-

from typing import Dict

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import Field

from apps.development.models import Issue
from apps.development.models.ticket import (
    TICKET_TYPE_MAX_LENGTH,
    TICKET_TYPES,
    Ticket,
)

ISSUES_PARAM_ERROR = 'Please, choose one parameter: "attachIssues" or "issues"'


class TicketBaseSerializer(serializers.ModelSerializer):
    """Ticket base serializer."""

    # we should redefine this field because django-graphene has a bug with a
    # choice fields. It creates enums types for these which leads to an error:
    # "AssertionError: Found different types with the same name in the schema:
    # type, type."
    type = serializers.CharField(  # noqa: A003
        required=False,
        max_length=TICKET_TYPE_MAX_LENGTH,
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
            'type', 'title', 'start_date', 'due_date', 'url', 'milestone',
            'issues',
        ]

    def get_fields(self) -> Dict[str, Field]:
        """Returns serializer fields."""
        fields = super().get_fields()

        if self.context:
            issues_qs = Issue.objects.allowed_for_user(
                self.context['request'].user,
            )
            fields['issues'].child_relation.queryset = issues_qs
        return fields

    def validate_type(self, type_):
        """Validates type is one of the valid choices."""
        if type_ and type_ not in TICKET_TYPES.keys():
            raise ValidationError(
                'type should be one of available choices: {0}'.format(
                    ', '.join(TICKET_TYPES.keys()),
                ),
            )

        return type_


class TicketCreateSerializer(TicketBaseSerializer):
    """Ticket create serializer."""


class TicketUpdateSerializer(TicketBaseSerializer):
    """Ticket update serializer."""

    id = serializers.CharField()  # noqa: A003
    attach_issues = serializers.PrimaryKeyRelatedField(
        many=True,
        required=False,
        write_only=True,
        queryset=Issue.objects,
    )

    class Meta(TicketBaseSerializer.Meta):
        fields = ['id', *TicketBaseSerializer.Meta.fields, 'attach_issues']

    def get_fields(self) -> Dict[str, Field]:
        """Returns serializer fields."""
        fields = super().get_fields()

        for name, field in fields.items():
            if name == 'id':
                field.required = True
                field.read_only = False
            else:
                field.required = False

        if self.context:
            issues_qs = Issue.objects.allowed_for_user(
                self.context['request'].user,
            )
            fields['attach_issues'].child_relation.queryset = issues_qs

        return fields

    def update(self, instance, validated_data):
        """Updates ticket and returns updated object."""
        attach_issues = validated_data.pop('attach_issues', None)
        issues = validated_data.pop('issues', None)

        ticket = super().update(instance, validated_data)

        if attach_issues:
            ticket.issues.add(*attach_issues)

        if issues:
            Issue.objects.filter(ticket=ticket).update(ticket=None)
            ticket.issues.add(*issues)

        return ticket

    def validate(self, attrs):
        """Validates input parameters."""
        if attrs.get('issues') and attrs.get('attach_issues'):
            raise ValidationError(ISSUES_PARAM_ERROR)

        return attrs
