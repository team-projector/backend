from apps.development.graphql.fields.tickets import TicketsFilterSet
from apps.development.models import Ticket
from tests.test_development.factories import (
    ProjectMilestoneFactory,
    TicketFactory,
)


def test_filter(db):
    """
    Test filter.

    :param db:
    """
    milestones = ProjectMilestoneFactory.create_batch(2)
    TicketFactory.create(milestone=milestones[0])
    TicketFactory.create(milestone=milestones[1])

    for milestone in milestones:
        tickets = TicketsFilterSet(
            data={"milestone": milestone.pk},
            queryset=Ticket.objects.all(),
        ).qs

        assert tickets.count() == 1
        assert tickets.first().milestone == milestone
