# -*- coding: utf-8 -*-

import pytest

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.core.utils.time import seconds
from apps.development.graphql.types import TicketType
from apps.development.models.issue import IssueState
from apps.development.services.ticket.metrics import get_ticket_metrics
from tests.test_development.factories import IssueFactory, TicketFactory
from tests.test_users.factories.user import UserFactory


def test_metrics_without_issues(db):
    ticket = TicketFactory.create()

    metrics = get_ticket_metrics(ticket)

    assert metrics.issues_count == 0
    assert metrics.time_spent == 0


def test_metrics(db):
    ticket = TicketFactory.create()

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


def test_budget_estimated(db):
    ticket = TicketFactory.create()

    user_1 = UserFactory.create(customer_hour_rate=3)

    IssueFactory.create(
        ticket=ticket,
        user=user_1,
        state=IssueState.OPENED,
        total_time_spent=0,
        time_estimate=seconds(hours=1),
    )
    IssueFactory.create(
        ticket=ticket,
        user=user_1,
        state=IssueState.CLOSED,
        total_time_spent=seconds(hours=1),
        time_estimate=seconds(hours=2),
    )

    user_2 = UserFactory.create(customer_hour_rate=5)

    IssueFactory.create(
        ticket=ticket,
        user=user_2,
        state=IssueState.OPENED,
        total_time_spent=0,
        time_estimate=seconds(hours=1),
    )
    IssueFactory.create(
        ticket=ticket,
        user=user_2,
        state=IssueState.CLOSED,
        total_time_spent=seconds(hours=2),
        time_estimate=seconds(hours=1),
    )

    IssueFactory.create(
        ticket=TicketFactory.create(),
        user=user_2,
        state=IssueState.OPENED,
        total_time_spent=seconds(hours=10),
        time_estimate=seconds(hours=10),
    )

    metrics = get_ticket_metrics(ticket)

    assert metrics.issues_count == 4
    assert metrics.time_estimate == seconds(hours=5)
    assert metrics.budget_estimate == 19


def test_resolve_metrics(user, ghl_auth_mock_info):
    user.roles.MANAGER = True
    user.save()

    ticket = TicketFactory.create()

    IssueFactory.create(
        ticket=ticket,
        state=IssueState.OPENED,
        total_time_spent=0,
        time_estimate=seconds(hours=1),
    )

    metrics = TicketType.resolve_metrics(ticket, info=ghl_auth_mock_info)

    assert metrics.issues_count == 1
    assert metrics.time_estimate == seconds(hours=1)


def test_resolve_metrics_not_pm(user, ghl_auth_mock_info):
    ticket = TicketFactory.create()

    IssueFactory.create(
        ticket=ticket,
        state=IssueState.OPENED,
        total_time_spent=0,
        time_estimate=seconds(hours=1),
    )

    with pytest.raises(GraphQLPermissionDenied):
        TicketType.resolve_metrics(ticket, info=ghl_auth_mock_info)


def test_opened_time_remains_without_issues(user, ghl_auth_mock_info):
    user.roles.MANAGER = True
    user.save()

    ticket = TicketFactory.create()

    metrics = TicketType.resolve_metrics(ticket, info=ghl_auth_mock_info)

    assert metrics.issues_count == 0
    assert metrics.opened_time_remains == 0


def test_opened_time_remains_with_closed_issues(user, ghl_auth_mock_info):
    user.roles.MANAGER = True
    user.save()

    ticket = TicketFactory.create()

    IssueFactory.create_batch(
        size=3, ticket=ticket, state=IssueState.CLOSED,
    )

    metrics = TicketType.resolve_metrics(ticket, info=ghl_auth_mock_info)

    assert metrics.issues_opened_count == 0
    assert metrics.opened_time_remains == 0
    assert metrics.time_estimate > 0
    assert metrics.time_spent > 0


def test_opened_time_remains(user, ghl_auth_mock_info):
    user.roles.MANAGER = True
    user.save()

    ticket = TicketFactory.create()

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

    metrics = TicketType.resolve_metrics(ticket, info=ghl_auth_mock_info)

    assert metrics.issues_opened_count == 2
    assert metrics.opened_time_remains == -3600


def test_opened_time_remains_random(user, ghl_auth_mock_info):
    user.roles.MANAGER = True
    user.save()

    ticket = TicketFactory.create()

    issues = IssueFactory.create_batch(
        size=3, ticket=ticket, state=IssueState.OPENED,
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

    metrics = TicketType.resolve_metrics(ticket, info=ghl_auth_mock_info)

    assert metrics.issues_opened_count == 3
    assert metrics.opened_time_remains == opened_time_remains
