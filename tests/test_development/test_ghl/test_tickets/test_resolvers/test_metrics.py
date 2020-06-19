# -*- coding: utf-8 -*-

import pytest
from jnt_django_toolbox.helpers.time import seconds

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.development.graphql.types import TicketType
from apps.development.models.issue import IssueState
from tests.test_development.factories import IssueFactory, TicketFactory


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
