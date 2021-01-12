import django_filters
import graphene
from jnt_django_graphene_toolbox.fields import BaseModelConnectionField

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


class TicketSort(graphene.Enum):
    """Allowed sort fields."""

    DUE_DATE_ASC = "due_date"  # noqa: WPS115
    DUE_DATE_DESC = "-due_date"  # noqa: WPS115
    START_DATE_ASC = "start_date"  # noqa: WPS115
    START_DATE_DESC = "-start_date"  # noqa: WPS115
    TITLE_ASC = "title"  # noqa: WPS115
    TITLE_DESC = "-title"  # noqa: WPS115
    STATE_ASC = "state"  # noqa: WPS115
    STATE_DESC = "-state"  # noqa: WPS115


class TicketsConnectionField(BaseModelConnectionField):
    """Handler for labels collections."""

    filterset_class = TicketsFilterSet
    auth_required = True

    def __init__(self):
        """Initialize."""
        super().__init__(
            "apps.development.graphql.types.TicketType",
            order_by=graphene.Argument(graphene.List(TicketSort)),
            milestone=graphene.ID(),
            state=graphene.Argument(graphene.Enum.from_enum(TicketState)),
        )
