from datetime import datetime, timedelta

import pytest

from apps.development.graphql.fields.tickets import (
    TicketsConnectionField,
    TicketSort,
)
from apps.development.models import Ticket
from apps.development.models.ticket import TicketState
from tests.helpers import lists
from tests.test_development.factories import TicketFactory


@pytest.fixture()
def sort_handler():
    """Sort handler."""
    return TicketsConnectionField.sort_handler


@pytest.mark.parametrize(
    ("sort", "indexes"),
    [
        (TicketSort.DUE_DATE_ASC, (0, 2, 1)),
        (TicketSort.DUE_DATE_DESC, (1, 2, 0)),
    ],
)
def test_by_due_date(db, sort, sort_handler, indexes):
    """Test ordering by date asc."""
    tickets = [
        TicketFactory.create(due_date=datetime.now() - timedelta(days=1)),
        TicketFactory.create(due_date=datetime.now() + timedelta(days=1)),
        TicketFactory.create(due_date=datetime.now()),
    ]

    queryset = sort_handler.filter(
        Ticket.objects.all(),
        [sort.value],
    )

    assert list(queryset) == lists.sub_list(tickets, indexes)


@pytest.mark.parametrize(
    ("sort", "indexes"),
    [
        (TicketSort.TITLE_ASC, (1, 0, 2)),
        (TicketSort.TITLE_DESC, (2, 0, 1)),
    ],
)
def test_by_title(db, sort, sort_handler, indexes):
    """Test ordering by title asc."""
    tickets = [
        TicketFactory.create(title="BB"),
        TicketFactory.create(title="AA"),
        TicketFactory.create(title="CC"),
    ]

    queryset = sort_handler.filter(
        Ticket.objects.all(),
        [sort.value],
    )

    assert list(queryset) == lists.sub_list(tickets, indexes)


def test_by_due_date_and_title(db, sort_handler):
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

    queryset = sort_handler.filter(
        Ticket.objects.all(),
        [TicketSort.DUE_DATE_ASC.value, TicketSort.TITLE_ASC.value],
    )

    assert queryset.count() == 3
    assert list(queryset) == lists.sub_list(tickets, (1, 0, 2))


@pytest.mark.parametrize(
    ("sort", "indexes"),
    [
        (TicketSort.STATE_ASC, (0, 2, 1)),
        (TicketSort.STATE_DESC, (1, 2, 0)),
    ],
)
def test_order_by_state(db, sort, sort_handler, indexes):
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

    queryset = sort_handler.filter(
        Ticket.objects.all(),
        [sort.value],
    )

    assert queryset.count() == 3
    assert list(queryset) == lists.sub_list(tickets, indexes)
