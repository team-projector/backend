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
    permission_classes = (AllowProjectManager,)
    form_class = TicketForm

    class Arguments:
        type = graphene.String(required=True)
        title = graphene.String(required=True)
        start_date = graphene.Date(required=True)
        due_date = graphene.Date(required=True)
        url = graphene.String(required=True)
        milestone = graphene.ID()

    ticket = graphene.Field(TicketType)

    @classmethod
    def perform_mutate(cls, info, data):
        ticket = Ticket.objects.create(**data)

        return CreateTicketMutation(
            ticket=ticket,
        )


class UpdateTicketMutation(
    ArgumentsValidationMixin,
    BaseMutation,
):
    permission_classes = (AllowProjectManager,)
    form_class = TicketForm

    class Arguments:
        id = graphene.ID(required=True)
        type = graphene.String()
        title = graphene.String()
        start_date = graphene.Date()
        due_date = graphene.Date()
        url = graphene.String()
        milestone = graphene.ID()

    ticket = graphene.Field(TicketType)

    @classmethod
    def perform_mutate(cls, info, data):
        ticket = get_object_or_404(
            Ticket.objects.all(),
            pk=data['id'],
        )

        cls._update_ticket(ticket, data)

        return UpdateTicketMutation(
            ticket=ticket,
        )

    @classmethod
    def _update_ticket(cls, ticket, data):
        if data.get('title'):
            ticket.title = data['title']

        if data.get('type'):
            ticket.type = data['type']

        if data.get('start_date'):
            ticket.start_date = data['start_date']

        if data.get('due_date'):
            ticket.due_date = data['due_date']

        if data.get('milestone'):
            ticket.milestone = data['milestone']

        ticket.save()

        return UpdateTicketMutation(ticket=ticket)
