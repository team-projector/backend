# -*- coding: utf-8 -*-

import pytest

from apps.core.graphql.errors import GraphQLPermissionDenied
from tests.test_development.factories import TicketFactory

GHL_QUERY_ALL_TICKETS = """
query {
  allTickets {
    count
    edges {
      node {
        id
        title
      }
    }
  }
}
"""


def test_query(user, ghl_client):
    """Test getting all tickets raw query."""
    TicketFactory.create_batch(5)

    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_ALL_TICKETS,
    )

    assert "errors" not in response
    assert response["data"]["allTickets"]["count"] == 5


def test_success(ghl_auth_mock_info, all_tickets_query):
    """Test success tickets list."""
    TicketFactory.create_batch(5)

    response = all_tickets_query(
        root=None,
        info=ghl_auth_mock_info,
    )

    assert response.length == 5


def test_unauth(ghl_mock_info, all_tickets_query):
    """Test unauth tickets list."""
    with pytest.raises(GraphQLPermissionDenied):
        all_tickets_query(
            root=None,
            info=ghl_mock_info,
        )
