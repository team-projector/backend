import django_filters
from jnt_django_graphene_toolbox.filters import OrderingFilter

from apps.development.models import Milestone, Ticket
from apps.development.models.ticket import TicketState


class TicketsFilterSet(django_filters.FilterSet):
    """Set of filters for Ticket."""

    class Meta:
        model = Ticket
        fields = ("milestone", "state")

    milestone = django_filters.ModelChoiceFilter(
        queryset=Milestone.objects.all(),
    )
    order_by = OrderingFilter(
        fields=("due_date", "start_date", "title", "state"),
    )
