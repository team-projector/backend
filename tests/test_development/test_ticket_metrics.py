from apps.core.utils.time import seconds
from apps.development.graphql.types import TicketType
from apps.development.models.issue import STATE_OPENED, STATE_CLOSED
from apps.development.services.metrics.ticket import get_ticket_metrics
from tests.test_development.factories import IssueFactory, TicketFactory


def test_metrics(db):
    ticket = TicketFactory.create()

    IssueFactory.create(
        ticket=ticket,
        state=STATE_OPENED,
        total_time_spent=0,
        time_estimate=seconds(hours=1)
    )
    IssueFactory.create(
        ticket=ticket,
        state=STATE_CLOSED,
        total_time_spent=seconds(hours=1),
        time_estimate=seconds(hours=2)
    )
    IssueFactory.create(
        ticket=ticket,
        state=STATE_CLOSED,
        total_time_spent=seconds(hours=2),
        time_estimate=seconds(hours=2)
    )

    metrics = get_ticket_metrics(ticket)

    assert metrics.issues_count == 3
    assert metrics.issues_closed_count == 2
    assert metrics.issues_opened_count == 1
    assert metrics.time_estimate == seconds(hours=5)
    assert metrics.time_spent == seconds(hours=3)


def test_resolver(db):
    ticket = TicketFactory.create()

    IssueFactory.create(
        ticket=ticket,
        state=STATE_OPENED,
        total_time_spent=0,
        time_estimate=seconds(hours=1)
    )

    metrics = TicketType.resolve_metrics(ticket, None)

    assert metrics.issues_count == 1
    assert metrics.time_estimate == seconds(hours=1)
