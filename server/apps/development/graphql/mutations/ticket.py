import graphene
from rest_framework.generics import get_object_or_404

from apps.core.graphql.mutations import BaseMutation
from apps.core.graphql.security.permissions import AllowProjectManager
from apps.development.graphql.types import TicketType
from apps.development.models import Ticket, Milestone


class CreateTicketMutation(BaseMutation):
    permission_classes = (AllowProjectManager,)

    class Arguments:
        title = graphene.String(required=True)
        type = graphene.String(required=True)
        start_date = graphene.Date(required=True)
        due_date = graphene.Date(required=True)
        milestone = graphene.ID(required=True)

    ticket = graphene.Field(TicketType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):
        milestone = get_object_or_404(
            Milestone.objects.all(),
            pk=kwargs['milestone']
        )

        kwargs['milestone'] = milestone
        ticket = Ticket.objects.create(**kwargs)

        return CreateTicketMutation(ticket=ticket)


class UpdateTicketMutation(BaseMutation):
    permission_classes = (AllowProjectManager,)

    class Arguments:
        id = graphene.ID()
        title = graphene.String()
        type = graphene.String()
        start_date = graphene.Date()
        due_date = graphene.Date()
        milestone = graphene.ID()

    ticket = graphene.Field(TicketType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):
        ticket = get_object_or_404(
            Ticket.objects.all(),
            pk=kwargs['id']
        )

        if kwargs.get('milestone'):
            milestone = get_object_or_404(
                Milestone.objects.all(),
                pk=kwargs['milestone']
            )

            kwargs['milestone'] = milestone

        cls._update_ticket(ticket, kwargs)

        return UpdateTicketMutation(
            ticket=ticket
        )

    @classmethod
    def _update_ticket(cls, ticket, data):
        if 'title' in data:
            ticket.title = data['title']

        if 'type' in data:
            ticket.type = data['type']

        if 'start_date' in data:
            ticket.start_date = data['start_date']

        if 'due_date' in data:
            ticket.due_date = data['due_date']

        if 'milestone' in data:
            ticket.milestone = data['milestone']

        ticket.save()
