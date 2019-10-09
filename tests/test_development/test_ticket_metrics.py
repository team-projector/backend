from pytest import raises
from django.core.exceptions import PermissionDenied

from apps.core.utils.time import seconds
from apps.development.graphql.types import TicketType
from apps.development.models.issue import ISSUE_STATES
from apps.development.services.metrics.ticket import get_ticket_metrics
from tests.test_development.factories import IssueFactory, TicketFactory
from tests.test_development.factories_gitlab import AttrDict
from tests.test_users.factories import UserFactory


def test_metrics(db):
    ticket = TicketFactory.create()

    IssueFactory.create(
        ticket=ticket,
        state=ISSUE_STATES.opened,
        total_time_spent=0,
        time_estimate=seconds(hours=1)
    )
    IssueFactory.create(
        ticket=ticket,
        state=ISSUE_STATES.closed,
        total_time_spent=seconds(hours=1),
        time_estimate=seconds(hours=2)
    )
    IssueFactory.create(
        ticket=ticket,
        state=ISSUE_STATES.closed,
        total_time_spent=seconds(hours=2),
        time_estimate=seconds(hours=2)
    )

    metrics = get_ticket_metrics(ticket)

    assert metrics.issues_count == 3
    assert metrics.issues_closed_count == 2
    assert metrics.issues_opened_count == 1
    assert metrics.time_spent == seconds(hours=3)


def test_budget_estimated(db):
    ticket = TicketFactory.create()

    user_1 = UserFactory.create(customer_hour_rate=3)

    IssueFactory.create(
        ticket=ticket,
        user=user_1,
        state=ISSUE_STATES.opened,
        total_time_spent=0,
        time_estimate=seconds(hours=1)
    )
    IssueFactory.create(
        ticket=ticket,
        user=user_1,
        state=ISSUE_STATES.closed,
        total_time_spent=seconds(hours=1),
        time_estimate=seconds(hours=2)
    )

    user_2 = UserFactory.create(customer_hour_rate=5)

    IssueFactory.create(
        ticket=ticket,
        user=user_2,
        state=ISSUE_STATES.opened,
        total_time_spent=0,
        time_estimate=seconds(hours=1)
    )
    IssueFactory.create(
        ticket=ticket,
        user=user_2,
        state=ISSUE_STATES.closed,
        total_time_spent=seconds(hours=2),
        time_estimate=seconds(hours=1)
    )

    IssueFactory.create(
        ticket=TicketFactory.create(),
        user=user_2,
        state=ISSUE_STATES.opened,
        total_time_spent=seconds(hours=10),
        time_estimate=seconds(hours=10)
    )

    metrics = get_ticket_metrics(ticket)

    assert metrics.issues_count == 4
    assert metrics.time_estimate == seconds(hours=5)
    assert metrics.budget_estimate == 19


def test_resolve_metrics(user, client):
    user.roles.project_manager = True
    user.save()

    ticket = TicketFactory.create()

    IssueFactory.create(
        ticket=ticket,
        state=ISSUE_STATES.opened,
        total_time_spent=0,
        time_estimate=seconds(hours=1)
    )

    client.user = user
    info = AttrDict({'context': client})

    metrics = TicketType.resolve_metrics(ticket, info=info)

    assert metrics.issues_count == 1
    assert metrics.time_estimate == seconds(hours=1)


def test_resolve_metrics_not_pm(user, client):
    ticket = TicketFactory.create()

    IssueFactory.create(
        ticket=ticket,
        state=ISSUE_STATES.opened,
        total_time_spent=0,
        time_estimate=seconds(hours=1)
    )

    client.user = user
    info = AttrDict({'context': client})

    with raises(PermissionDenied):
        TicketType.resolve_metrics(ticket, info=info)
