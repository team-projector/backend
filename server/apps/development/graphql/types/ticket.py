import graphene
from django.db.models import QuerySet

from apps.core import graphql
from apps.core.graphql.types import BaseModelObjectType
from apps.development.graphql.fields import IssuesConnectionField
from apps.development.graphql.types import MilestoneType, TicketMetricsType
from apps.development.models import Ticket
from apps.development.models.ticket import TicketState
from apps.development.models.ticket import TicketType as ModelTicketType
from apps.development.services.ticket import allowed, metrics
from apps.development.services.ticket.problems import (
    annotate_ticket_problems,
    get_ticket_problems,
)


class TicketType(BaseModelObjectType):
    """Class represents list of available fields for ticket queries."""

    class Meta:
        model = Ticket

    created_at = graphene.DateTime()
    metrics = graphene.Field(TicketMetricsType)
    problems = graphene.List(graphene.String)
    issues = IssuesConnectionField()
    type = graphene.Field(  # noqa: WPS125, A003
        graphene.Enum.from_enum(ModelTicketType),
    )
    title = graphene.String()
    start_date = graphene.Date()
    due_date = graphene.Date()
    url = graphene.String()
    role = graphene.String()
    estimate = graphene.Int()
    state = graphene.Field(
        graphene.Enum.from_enum(TicketState),
    )
    milestone = graphene.Field(MilestoneType)

    @classmethod
    def get_queryset(cls, queryset, info) -> QuerySet:  # noqa: WPS110
        """Get tickets."""
        if graphql.is_field_selected(info, "edges.node.problems"):
            queryset = annotate_ticket_problems(queryset)

        return queryset

    def resolve_metrics(self, info, **kwargs):  # noqa: WPS110
        """Get metrics."""
        allowed.check_project_manager(info.context.user)
        return metrics.get_ticket_metrics(self)

    def resolve_problems(self, info, **kwargs):  # noqa: WPS110
        """Get ticket problems."""
        return get_ticket_problems(self)
