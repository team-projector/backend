import django_filters
import graphene

from apps.core.graphql.fields import BaseModelConnectionField
from apps.core.graphql.queries.filters import OrderingFilter
from apps.development.models import Milestone, Ticket
from apps.development.models.ticket import TicketState


class TicketsFilterSet(django_filters.FilterSet):
    """Set of filters for Ticket."""

    class Meta:
        model = Ticket
        fields = "__all__"

    milestone = django_filters.ModelChoiceFilter(
        queryset=Milestone.objects.all(),
    )
    order_by = OrderingFilter(
        fields=("due_date", "start_date", "title", "state"),
    )


class TicketsConnectionField(BaseModelConnectionField):
    """Handler for labels collections."""

    filterset_class = TicketsFilterSet
    auth_required = True

    def __init__(self):
        """Initialize."""
        super().__init__(
            "apps.development.graphql.types.TicketType",
            order_by=graphene.String(),
            milestone=graphene.ID(),
            state=graphene.Argument(graphene.Enum.from_enum(TicketState)),
        )
