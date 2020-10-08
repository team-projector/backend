import pytest
from jnt_django_toolbox.helpers.time import seconds

from apps.development.models.issue import IssueState
from apps.development.services.ticket.metrics import get_ticket_metrics
from tests.test_development.factories import IssueFactory, TicketFactory
from tests.test_users.factories.user import UserFactory


@pytest.fixture()
def ticket(db):
    """
    Ticket.

    :param db:
    """
    return TicketFactory.create()


def test_metrics_without_issues(ticket):
    """
    Test metrics without issues.

    :param ticket:
    """
    metrics = get_ticket_metrics(ticket)

    assert metrics.issues_count == 0
    assert metrics.time_spent == 0
    assert metrics.opened_time_remains == 0


def test_metrics(ticket):
    """
    Test metrics.

    :param ticket:
    """
    IssueFactory.create(
        ticket=ticket,
        state=IssueState.OPENED,
        total_time_spent=0,
        time_estimate=seconds(hours=1),
    )
    IssueFactory.create(
        ticket=ticket,
        state=IssueState.CLOSED,
        total_time_spent=seconds(hours=1),
        time_estimate=seconds(hours=2),
    )
    IssueFactory.create(
        ticket=ticket,
        state=IssueState.CLOSED,
        total_time_spent=seconds(hours=2),
        time_estimate=seconds(hours=2),
    )

    metrics = get_ticket_metrics(ticket)

    assert metrics.issues_count == 3
    assert metrics.issues_closed_count == 2
    assert metrics.issues_opened_count == 1
    assert metrics.time_spent == seconds(hours=3)


def test_budget_estimated(ticket):
    """
    Test budget estimated.

    :param ticket:
    """
    user1 = UserFactory.create(customer_hour_rate=3)

    IssueFactory.create(
        ticket=ticket,
        user=user1,
        state=IssueState.OPENED,
        total_time_spent=0,
        time_estimate=seconds(hours=1),
    )
    IssueFactory.create(
        ticket=ticket,
        user=user1,
        state=IssueState.CLOSED,
        total_time_spent=seconds(hours=1),
        time_estimate=seconds(hours=2),
    )

    user2 = UserFactory.create(customer_hour_rate=5)

    IssueFactory.create(
        ticket=ticket,
        user=user2,
        state=IssueState.OPENED,
        total_time_spent=0,
        time_estimate=seconds(hours=1),
    )
    IssueFactory.create(
        ticket=ticket,
        user=user2,
        state=IssueState.CLOSED,
        total_time_spent=seconds(hours=2),
        time_estimate=seconds(hours=1),
    )

    IssueFactory.create(
        ticket=TicketFactory.create(),
        user=user2,
        state=IssueState.OPENED,
        total_time_spent=seconds(hours=10),
        time_estimate=seconds(hours=10),
    )

    metrics = get_ticket_metrics(ticket)

    assert metrics.issues_count == 4
    assert metrics.time_estimate == seconds(hours=5)
    assert metrics.budget_estimate == 19


def test_opened_time_remains_with_closed_issues(ticket):
    """
    Test opened time remains with closed issues.

    :param ticket:
    """
    IssueFactory.create_batch(
        size=3,
        ticket=ticket,
        state=IssueState.CLOSED,
    )

    metrics = get_ticket_metrics(ticket)

    assert metrics.issues_opened_count == 0
    assert metrics.opened_time_remains == 0
    assert metrics.time_estimate > 0
    assert metrics.time_spent > 0


def test_opened_time_remains(ticket):
    """
    Test opened time remains.

    :param ticket:
    """
    IssueFactory.create(
        ticket=ticket,
        state=IssueState.OPENED,
        total_time_spent=seconds(hours=5),
        time_estimate=seconds(hours=3),
    )

    IssueFactory.create(
        ticket=ticket,
        state=IssueState.OPENED,
        total_time_spent=seconds(hours=3),
        time_estimate=seconds(hours=4),
    )

    IssueFactory.create(
        ticket=ticket,
        state=IssueState.CLOSED,
        total_time_spent=seconds(hours=1),
        time_estimate=seconds(hours=4),
    )

    metrics = get_ticket_metrics(ticket)

    assert metrics.issues_opened_count == 2
    assert metrics.opened_time_remains == -3600


def test_opened_time_remains_random(ticket):
    """
    Test opened time remains random.

    :param ticket:
    """
    issues = IssueFactory.create_batch(
        size=3,
        ticket=ticket,
        state=IssueState.OPENED,
    )

    IssueFactory.create(
        ticket=ticket,
        state=IssueState.CLOSED,
        total_time_spent=seconds(hours=1),
        time_estimate=seconds(hours=4),
    )

    opened_time_remains = 0

    for issue in issues:
        opened_time_remains += issue.time_estimate
        opened_time_remains -= issue.total_time_spent

    metrics = get_ticket_metrics(ticket)

    assert metrics.issues_opened_count == 3
    assert metrics.opened_time_remains == opened_time_remains
