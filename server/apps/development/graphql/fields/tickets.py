import django_filters
import graphene
from jnt_django_graphene_toolbox.fields import BaseModelConnectionField
from jnt_django_graphene_toolbox.filters import SortHandler

from apps.development.graphql.types.enums import TicketState
from apps.development.models import Milestone, Ticket


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


class TicketsFilterSet(django_filters.FilterSet):
    """Set of filters for Ticket."""

    class Meta:
        model = Ticket
        fields = "__all__"

    state = django_filters.CharFilter()
    milestone = django_filters.ModelChoiceFilter(
        queryset=Milestone.objects.all(),
    )


class TicketsConnectionField(BaseModelConnectionField):
    """Handler for labels collections."""

    auth_required = True
    sort_handler = SortHandler(TicketSort)
    filterset_class = TicketsFilterSet

    def __init__(self):
        """Initialize."""
        super().__init__(
            "apps.development.graphql.types.TicketType",
            milestone=graphene.ID(),
            state=graphene.Argument(TicketState),
        )
