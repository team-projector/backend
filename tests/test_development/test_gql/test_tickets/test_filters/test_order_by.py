from datetime import datetime, timedelta

from apps.development.graphql.fields.tickets import TicketsFilterSet
from apps.development.models import Ticket
from apps.development.models.ticket import TicketState
from tests.helpers import lists
from tests.test_development.factories import TicketFactory

KEY_ORDERING = "order_by"


def test_by_due_date_asc(db):
    """Test ordering by date asc."""
    tickets = [
        TicketFactory.create(due_date=datetime.now() - timedelta(days=1)),
        TicketFactory.create(due_date=datetime.now() + timedelta(days=1)),
        TicketFactory.create(due_date=datetime.now()),
    ]

    queryset = TicketsFilterSet(
        data={KEY_ORDERING: "due_date"},
        queryset=Ticket.objects.all(),
    ).qs

    assert queryset.count() == 3
    assert list(queryset) == lists.sub_list(tickets, (0, 2, 1))


def test_by_due_date_desc(db):
    """Test ordering by date desc."""
    tickets = [
        TicketFactory.create(due_date=datetime.now() - timedelta(days=1)),
        TicketFactory.create(due_date=datetime.now() + timedelta(days=1)),
        TicketFactory.create(due_date=datetime.now()),
    ]

    queryset = TicketsFilterSet(
        data={KEY_ORDERING: "-due_date"},
        queryset=Ticket.objects.all(),
    ).qs

    assert queryset.count() == 3
    assert list(queryset) == lists.sub_list(tickets, (1, 2, 0))


def test_by_title_asc(db):
    """Test ordering by title asc."""
    tickets = [
        TicketFactory.create(title="BB"),
        TicketFactory.create(title="AA"),
        TicketFactory.create(title="CC"),
    ]

    queryset = TicketsFilterSet(
        data={KEY_ORDERING: "title"},
        queryset=Ticket.objects.all(),
    ).qs

    assert queryset.count() == 3
    assert list(queryset) == lists.sub_list(tickets, (1, 0, 2))


def test_by_title_desc(db):
    """Test ordering by title desc."""
    tickets = [
        TicketFactory.create(title="BB"),
        TicketFactory.create(title="AA"),
        TicketFactory.create(title="CC"),
    ]

    queryset = TicketsFilterSet(
        data={KEY_ORDERING: "-title"},
        queryset=Ticket.objects.all(),
    ).qs

    assert queryset.count() == 3
    assert list(queryset) == lists.sub_list(tickets, (2, 0, 1))


def test_by_due_date_and_title(db):
    """Test ordering by state."""
    tickets = [
        TicketFactory.create(
            title="BB",
        ),
        TicketFactory.create(
            title="AA",
        ),
        TicketFactory.create(
            title="CC",
        ),
    ]

    queryset = TicketsFilterSet(
        data={KEY_ORDERING: "due_date,title"},
        queryset=Ticket.objects.all(),
    ).qs

    assert queryset.count() == 3
    assert list(queryset) == lists.sub_list(tickets, (1, 0, 2))


def test_order_by_state(db):
    """Test complex ordering by date and title."""
    tickets = [
        TicketFactory.create(
            due_date=datetime.now() + timedelta(days=1),
            state=TicketState.CREATED,
        ),
        TicketFactory.create(
            due_date=datetime.now() + timedelta(days=1),
            state=TicketState.PLANNING,
        ),
        TicketFactory.create(
            due_date=datetime.now() + timedelta(days=2),
            state=TicketState.DOING,
        ),
    ]

    queryset = TicketsFilterSet(
        data={KEY_ORDERING: "state"},
        queryset=Ticket.objects.all(),
    ).qs

    assert queryset.count() == 3
    assert list(queryset) == lists.sub_list(tickets, (0, 2, 1))


def test_order_by_state_desc(db):
    """Test complex ordering by date and title."""
    tickets = [
        TicketFactory.create(
            due_date=datetime.now() + timedelta(days=1),
            state=TicketState.CREATED,
        ),
        TicketFactory.create(
            due_date=datetime.now() + timedelta(days=1),
            state=TicketState.PLANNING,
        ),
        TicketFactory.create(
            due_date=datetime.now() + timedelta(days=2),
            state=TicketState.DOING,
        ),
    ]

    queryset = TicketsFilterSet(
        data={KEY_ORDERING: "-state"},
        queryset=Ticket.objects.all(),
    ).qs

    assert queryset.count() == 3
    assert list(queryset) == lists.sub_list(tickets, (1, 2, 0))
