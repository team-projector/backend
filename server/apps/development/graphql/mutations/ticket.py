import graphene
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from apps.core.graphql.mutations import BaseMutation
from apps.core.graphql.security.permissions import AllowProjectManager
from apps.development.graphql.types import TicketType
from apps.development.models import Ticket, Milestone


class CreateTicketMutation(BaseMutation):
    permission_classes = (AllowProjectManager,)

    class Arguments:
        type = graphene.String(required=True)
        title = graphene.String(required=True)
        start_date = graphene.Date(required=True)
        due_date = graphene.Date(required=True)
        url = graphene.String(required=True)
        milestone = graphene.ID()

    ticket = graphene.Field(TicketType)

    @classmethod
    def do_mutate(cls, root, info, **kwargs):
        _validate_type(kwargs)
        _validate_milestone(kwargs)

        ticket = Ticket.objects.create(**kwargs)

        return CreateTicketMutation(ticket=ticket)


class UpdateTicketMutation(BaseMutation):
    permission_classes = (AllowProjectManager,)

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
    def do_mutate(cls, root, info, id, **kwargs):
        ticket = get_object_or_404(
            Ticket.objects.all(),
            pk=id
        )

        _validate_type(kwargs)
        _validate_milestone(kwargs)

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

        return UpdateTicketMutation(ticket=ticket)


def _validate_type(inputs: dict) -> None:
    if not inputs.get('type'):
        return

    if not inputs.get('type') in Ticket.TYPE.keys():
        raise ValidationError('Incorrect ticket type')


def _validate_milestone(inputs: dict) -> None:
    if not inputs.get('milestone'):
        return

    milestone = get_object_or_404(
        Milestone.objects.all(),
        pk=inputs['milestone']
    )

    inputs['milestone'] = milestone
