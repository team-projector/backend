# -*- coding: utf-8 -*-

import graphene
from rest_framework.generics import get_object_or_404

from apps.core.graphql.mutations import ArgumentsValidationMixin, BaseMutation
from apps.core.graphql.security.permissions import AllowProjectManager
from apps.development.graphql.forms import TicketForm
from apps.development.graphql.types import TicketType
from apps.development.models import Ticket


class CreateTicketMutation(
    ArgumentsValidationMixin,
    BaseMutation,
):
    """Create ticket mutation."""

    permission_classes = (AllowProjectManager,)
    form_class = TicketForm

    class Arguments:
        type = graphene.String(required=True)  # noqa A003
        title = graphene.String(required=True)
        start_date = graphene.Date(required=True)
        due_date = graphene.Date(required=True)
        url = graphene.String(required=True)
        milestone = graphene.ID()

    ticket = graphene.Field(TicketType)

    @classmethod
    def perform_mutate(cls, info, cleaned_data):  # noqa WPS110
        """Create and return ticket."""
        ticket = Ticket.objects.create(**cleaned_data)

        return CreateTicketMutation(
            ticket=ticket,
        )


class UpdateTicketMutation(
    ArgumentsValidationMixin,
    BaseMutation,
):
    """Update ticket mutation."""

    permission_classes = (AllowProjectManager,)
    form_class = TicketForm

    class Arguments:
        id = graphene.ID(required=True)  # noqa A003
        type = graphene.String()  # noqa A003
        title = graphene.String()
        start_date = graphene.Date()
        due_date = graphene.Date()
        url = graphene.String()
        milestone = graphene.ID()

    ticket = graphene.Field(TicketType)

    @classmethod
    def perform_mutate(cls, info, cleaned_data):  # noqa WPS110
        """Update and return ticket."""
        ticket = get_object_or_404(
            Ticket.objects.all(),
            pk=cleaned_data['id'],
        )

        cls._update_ticket(ticket, cleaned_data)

        return UpdateTicketMutation(
            ticket=ticket,
        )

    @classmethod  # noqa C901
    def _update_ticket(cls, ticket, cleaned_data):
        if cleaned_data.get('title'):
            ticket.title = cleaned_data['title']

        if cleaned_data.get('type'):
            ticket.type = cleaned_data['type']

        if cleaned_data.get('start_date'):
            ticket.start_date = cleaned_data['start_date']

        if cleaned_data.get('due_date'):
            ticket.due_date = cleaned_data['due_date']

        if cleaned_data.get('url'):
            ticket.url = cleaned_data['url']

        if cleaned_data.get('milestone'):
            ticket.milestone = cleaned_data['milestone']

        ticket.save()

        return UpdateTicketMutation(ticket=ticket)
