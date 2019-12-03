# -*- coding: utf-8 -*-

import graphene
from rest_framework.generics import get_object_or_404

from apps.core.graphql.mutations import (
    BaseMutation,
    RestrictedAccessSerializerMutation,
)
from apps.core.graphql.security.permissions import AllowProjectManager
from apps.development.graphql.serializers.ticket import (
    TicketCreateSerializer,
    TicketUpdateSerializer,
)
from apps.development.graphql.types import TicketType
from apps.development.models import Ticket


class BaseTicketMutation(RestrictedAccessSerializerMutation):
    """Base ticket mutation."""

    permission_classes = (AllowProjectManager,)
    ticket = graphene.Field(TicketType)

    class Meta:
        abstract = True

    @classmethod
    def perform_mutate(cls, serializer, info):  # noqa WPS110
        """Performs ticket mutation and returns a payload."""
        ticket = serializer.save()
        return cls(errors=None, ticket=ticket)


class CreateTicketMutation(BaseTicketMutation):
    """Create ticket mutation."""

    class Meta:
        serializer_class = TicketCreateSerializer


class UpdateTicketMutation(BaseTicketMutation):
    """Update ticket mutation."""

    class Meta:
        serializer_class = TicketUpdateSerializer


class DeleteTicketMutation(BaseMutation):
    """Delete ticket."""

    permission_classes = (AllowProjectManager,)

    class Arguments:
        id = graphene.ID(required=True)  # noqa A003

    ok = graphene.Boolean()

    @classmethod
    def do_mutate(cls, root, info, **kwargs):  # noqa WPS110
        """Delete ticket."""
        ticket = get_object_or_404(
            Ticket.objects.all(),
            pk=kwargs['id'],
        )

        ticket.delete()

        return DeleteTicketMutation(ok=True)
