from datetime import datetime, timedelta

import pytest

from apps.development.services.ticket.problems import (
    PROBLEM_OVER_DUE_DATE,
    get_ticket_problems,
)
from tests.test_development.factories import IssueFactory, TicketFactory


@pytest.fixture()
def ticket(user):
    """Create ticket."""
    due_date = datetime.now().date() - timedelta(days=2)

    ticket = TicketFactory.create(due_date=due_date)
    IssueFactory.create(
        user=user,
        ticket=ticket,
        due_date=due_date - timedelta(days=1),
    )

    return ticket


@pytest.fixture()
def ticket_over_due_date(user):
    """Create over due date ticket."""
    due_date = datetime.now().date() - timedelta(days=2)

    ticket = TicketFactory.create(due_date=due_date)
    IssueFactory.create(
        user=user,
        ticket=ticket,
        due_date=due_date + timedelta(days=1),
    )

    return ticket


def test_over_due_date_ticket(ticket, ticket_over_due_date):
    """Test not ready ticket."""
    assert get_ticket_problems(ticket_over_due_date) == [PROBLEM_OVER_DUE_DATE]


def test_no_problems(ticket, ticket_over_due_date):
    """Test no problems ticket ticket."""
    assert not get_ticket_problems(ticket)
