# -*- coding: utf-8 -*-

from typing import Any, Dict, Optional

import graphene
from graphql import ResolveInfo
from rest_framework.generics import get_object_or_404

from apps.core.graphql.helpers.persisters import update_from_validated_data
from apps.core.graphql.mutations import BaseMutation, SerializerMutation
from apps.core.graphql.security.permissions import AllowProjectManager
from apps.development.graphql.mutations.inputs.ticket_create import (
    TicketCreateInput,
)
from apps.development.graphql.mutations.inputs.ticket_update import (
    TicketUpdateInput,
)
from apps.development.graphql.types import TicketType
from apps.development.models import Issue, Ticket


class CreateTicketMutation(SerializerMutation):
    """Create ticket mutation."""

    ticket = graphene.Field(TicketType)
    permission_classes = (AllowProjectManager,)

    class Meta:
        serializer_class = TicketCreateInput

    @classmethod
    def perform_mutate(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110
        validated_data: Dict[str, Any],
    ) -> 'CreateTicketMutation':
        """Overrideable mutation operation."""
        issues = validated_data.pop('issues', None)
        ticket = Ticket.objects.create(**validated_data)

        if issues:
            ticket.issues.add(*issues)

        return cls(ticket=ticket)


class UpdateTicketMutation(SerializerMutation):
    """Update ticket mutation."""

    ticket = graphene.Field(TicketType)
    permission_classes = (AllowProjectManager,)

    class Meta:
        serializer_class = TicketUpdateInput

    @classmethod
    def perform_mutate(
        cls,
        root: Optional[object],
        info: ResolveInfo,  # noqa: WPS110ø
        validated_data: Dict[str, Any],
    ) -> 'UpdateTicketMutation':
        """Overrideable mutation operation."""
        ticket = validated_data.pop('ticket')
        attach_issues = validated_data.pop('attach_issues', None)
        issues = validated_data.pop('issues', None)

        update_from_validated_data(ticket, validated_data)

        if attach_issues:
            ticket.issues.add(*attach_issues)

        if issues is not None:
            Issue.objects.filter(ticket=ticket).exclude(
                id__in=[iss.id for iss in issues],
            ).update(ticket=None)

            ticket.issues.add(*issues)

        return cls(ticket=ticket)


class DeleteTicketMutation(BaseMutation):
    """Delete ticket."""

    permission_classes = (AllowProjectManager,)

    class Arguments:
        id = graphene.ID(required=True)  # noqa: A003

    ok = graphene.Boolean()

    @classmethod
    def do_mutate(cls, root, info, **kwargs):  # noqa: WPS110
        """Delete ticket."""
        ticket = get_object_or_404(
            Ticket.objects.all(),
            pk=kwargs['id'],
        )

        ticket.delete()

        return DeleteTicketMutation(ok=True)
