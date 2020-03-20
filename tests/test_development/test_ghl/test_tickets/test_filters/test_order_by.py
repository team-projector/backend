# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from apps.development.graphql.filters import TicketsFilterSet
from apps.development.models import Ticket
from tests import helpers
from tests.test_development.factories import TicketFactory


def test_by_due_date_asc(db):
    """Test ordering by date asc."""
    tickets = [
        TicketFactory.create(due_date=datetime.now() - timedelta(days=1)),
        TicketFactory.create(due_date=datetime.now() + timedelta(days=1)),
        TicketFactory.create(due_date=datetime.now()),
    ]

    results = TicketsFilterSet(
        data={"order_by": "dueDate"}, queryset=Ticket.objects.all(),
    ).qs

    assert results.count() == 3
    assert list(results) == helpers.sub_list(tickets, (0, 2, 1))


def test_by_due_date_desc(db):
    """Test ordering by date desc."""
    tickets = [
        TicketFactory.create(due_date=datetime.now() - timedelta(days=1)),
        TicketFactory.create(due_date=datetime.now() + timedelta(days=1)),
        TicketFactory.create(due_date=datetime.now()),
    ]

    results = TicketsFilterSet(
        data={"order_by": "-dueDate"}, queryset=Ticket.objects.all(),
    ).qs

    assert results.count() == 3
    assert list(results) == helpers.sub_list(tickets, (1, 2, 0))


def test_by_title_asc(db):
    """Test ordering by title asc."""
    tickets = [
        TicketFactory.create(title="BB"),
        TicketFactory.create(title="AA"),
        TicketFactory.create(title="CC"),
    ]

    results = TicketsFilterSet(
        data={"order_by": "title"}, queryset=Ticket.objects.all(),
    ).qs

    assert results.count() == 3
    assert list(results) == helpers.sub_list(tickets, (1, 0, 2))


def test_by_title_desc(db):
    """Test ordering by title desc."""
    tickets = [
        TicketFactory.create(title="BB"),
        TicketFactory.create(title="AA"),
        TicketFactory.create(title="CC"),
    ]

    results = TicketsFilterSet(
        data={"order_by": "-title"}, queryset=Ticket.objects.all(),
    ).qs

    assert results.count() == 3
    assert list(results) == helpers.sub_list(tickets, (2, 0, 1))


def test_by_due_date_and_title(db):
    """Test complex ordering by date and title."""
    tickets = [
        TicketFactory.create(
            due_date=datetime.now() + timedelta(days=1), title="BB"
        ),
        TicketFactory.create(
            due_date=datetime.now() + timedelta(days=1), title="AA"
        ),
        TicketFactory.create(
            due_date=datetime.now() + timedelta(days=2), title="CC"
        ),
    ]

    results = TicketsFilterSet(
        data={"order_by": "dueDate,title"}, queryset=Ticket.objects.all(),
    ).qs

    assert results.count() == 3
    assert list(results) == helpers.sub_list(tickets, (1, 0, 2))