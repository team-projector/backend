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
    def do_mutate(cls, root, info, id, **kwargs):
        ticket = get_object_or_404(
            Ticket.objects.all(),
            pk=id
        )

        if kwargs.get('milestone'):
            milestone = get_object_or_404(
                Milestone.objects.all(),
                pk=kwargs['milestone']
            )

            kwargs['milestone'] = milestone

        for attr, value in kwargs.items():
            setattr(ticket, attr, value)
        ticket.save()

        return UpdateTicketMutation(ticket=ticket)
