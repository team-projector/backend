import graphene

from apps.development.models.ticket import TicketState as ModelTicketState

TicketState = graphene.Enum.from_enum(ModelTicketState)
