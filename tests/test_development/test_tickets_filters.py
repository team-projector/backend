from apps.development.graphql.filters import TicketsFilterSet
from apps.development.models import Ticket
from tests.test_development.factories import (
    TicketFactory, ProjectMilestoneFactory,
)


def test_filter_by_milestone(user):
    milestone_1 = ProjectMilestoneFactory.create()
    TicketFactory.create(milestone=milestone_1)

    milestone_2 = ProjectMilestoneFactory.create()
    TicketFactory.create(milestone=milestone_2)

    results = TicketsFilterSet(
        data={'milestone': milestone_1.id},
        queryset=Ticket.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first().milestone == milestone_1

    results = TicketsFilterSet(
        data={'milestone': milestone_2.id},
        queryset=Ticket.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first().milestone == milestone_2
