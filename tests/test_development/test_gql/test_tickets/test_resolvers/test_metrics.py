import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied
from jnt_django_toolbox.helpers.time import seconds

from apps.development.graphql.types import TicketType
from apps.development.models.issue import IssueState
from apps.users.models import User
from tests.test_development.factories import IssueFactory, TicketFactory


def test_resolve_metrics(user, ghl_auth_mock_info):
    """
    Test resolve metrics.

    :param user:
    :param ghl_auth_mock_info:
    """
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
    """
    Test resolve metrics not pm.

    :param user:
    :param ghl_auth_mock_info:
    """
    user.roles = User.roles.DEVELOPER
    user.save()

    ticket = TicketFactory.create()

    IssueFactory.create(
        ticket=ticket,
        state=IssueState.OPENED,
        total_time_spent=0,
        time_estimate=seconds(hours=1),
    )

    with pytest.raises(GraphQLPermissionDenied):
        TicketType.resolve_metrics(ticket, info=ghl_auth_mock_info)
