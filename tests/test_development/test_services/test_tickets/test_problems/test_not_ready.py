import pytest

from apps.development.services.ticket.problems import (
    UNASSIGNED_ISSUES,
    get_ticket_problems,
)
from tests.test_development.factories import IssueFactory, TicketFactory


@pytest.fixture()
def ticket(user):
    """Create ticket."""
    ticket = TicketFactory.create()
    IssueFactory.create(user=user, ticket=ticket)

    return ticket


@pytest.fixture()
def ticket_not_ready(db):
    """Create not ready ticket."""
    ticket = TicketFactory.create()
    IssueFactory.create(user=None, ticket=ticket)

    return ticket


def test_not_ready_ticket(ticket, ticket_not_ready):
    """Test not ready ticket."""
    assert get_ticket_problems(ticket_not_ready) == [UNASSIGNED_ISSUES]


def test_no_problems(ticket, ticket_not_ready):
    """Test no problems ticket ticket."""
    assert not get_ticket_problems(ticket)
