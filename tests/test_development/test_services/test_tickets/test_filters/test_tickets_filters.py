from datetime import datetime, timedelta

from apps.development.graphql.filters import TicketsFilterSet
from apps.development.models import Ticket
from tests.test_development.factories import (
    ProjectMilestoneFactory,
    TicketFactory,
)


def test_filter_by_milestone(db):
    milestone_1 = ProjectMilestoneFactory.create()
    TicketFactory.create(milestone=milestone_1)

    milestone_2 = ProjectMilestoneFactory.create()
    TicketFactory.create(milestone=milestone_2)

    results = TicketsFilterSet(
        data={"milestone": milestone_1.id},
        queryset=Ticket.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first().milestone == milestone_1

    results = TicketsFilterSet(
        data={"milestone": milestone_2.id},
        queryset=Ticket.objects.all(),
    ).qs

    assert results.count() == 1
    assert results.first().milestone == milestone_2


def test_order_by_due_date(db):
    ticket_1 = TicketFactory.create(
        due_date=datetime.now() - timedelta(days=1)
    )
    ticket_2 = TicketFactory.create(
        due_date=datetime.now() + timedelta(days=1)
    )
    ticket_3 = TicketFactory.create(
        due_date=datetime.now()
    )

    results = TicketsFilterSet(
        data={"order_by": "dueDate"},
        queryset=Ticket.objects.all(),
    ).qs

    assert results.count() == 3
    assert list(results) == [ticket_1, ticket_3, ticket_2]

    results = TicketsFilterSet(
        data={"order_by": "-dueDate"},
        queryset=Ticket.objects.all(),
    ).qs

    assert list(results) == [ticket_2, ticket_3, ticket_1]


def test_order_by_title(db):
    ticket_1 = TicketFactory.create(title="BB")
    ticket_2 = TicketFactory.create(title="AA")
    ticket_3 = TicketFactory.create(title="CC")

    results = TicketsFilterSet(
        data={"order_by": "title"},
        queryset=Ticket.objects.all(),
    ).qs

    assert results.count() == 3
    assert list(results) == [ticket_2, ticket_1, ticket_3]

    results = TicketsFilterSet(
        data={"order_by": "-title"},
        queryset=Ticket.objects.all(),
    ).qs

    assert list(results) == [ticket_3, ticket_1, ticket_2]


def test_order_by_due_date_and_title(db):
    ticket_1 = TicketFactory.create(
        due_date=datetime.now() + timedelta(days=1), title="BB"
    )
    ticket_2 = TicketFactory.create(
        due_date=datetime.now() + timedelta(days=1), title="AA"
    )
    ticket_3 = TicketFactory.create(
        due_date=datetime.now() + timedelta(days=2), title="CC"
    )

    results = TicketsFilterSet(
        data={"order_by": "dueDate,title"},
        queryset=Ticket.objects.all(),
    ).qs

    assert results.count() == 3
    assert list(results) == [ticket_2, ticket_1, ticket_3]
