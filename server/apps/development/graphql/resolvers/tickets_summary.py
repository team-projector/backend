from jnt_django_graphene_toolbox.helpers.selected_fields import (
    get_fields_from_info,
)

from apps.development.graphql.fields.tickets import TicketsFilterSet
from apps.development.models import Ticket
from apps.development.services.ticket.summary import TicketsSummaryProvider


def resolve_tickets_summary(
    parent,
    info,  # noqa: WPS110
    **kwargs,
):
    """Resolve issues summary."""
    filterset = TicketsFilterSet(
        data=kwargs,
        queryset=Ticket.objects.all(),
        request=info.context,
    )

    return TicketsSummaryProvider(
        filterset.qs,
        fields=get_fields_from_info(info),
    ).get_data()
