import pytest
from jnt_django_graphene_toolbox.errors import (
    GraphQLNotFound,
    GraphQLPermissionDenied,
)

from tests.test_development.factories import TicketFactory

GHL_QUERY_TICKET = """
query ($id: ID!) {
  ticket (id: $id) {
    id
    title
  }
}
"""


def test_query(user, ghl_client):
    """Test getting ticket raw query."""
    ticket = TicketFactory.create()

    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_TICKET,
        variable_values={"id": ticket.pk},
    )

    assert "errors" not in response
    assert response["data"]["ticket"]["id"] == str(ticket.pk)


def test_success(ghl_auth_mock_info, ticket_query):
    """Test success ticket retrieving."""
    ticket = TicketFactory.create()

    response = ticket_query(root=None, info=ghl_auth_mock_info, id=ticket.pk)

    assert response.id == ticket.pk


def test_unauth(db, ghl_mock_info, ticket_query):
    """Test unauth ticket retrieving."""
    ticket = TicketFactory.create()

    with pytest.raises(GraphQLPermissionDenied):
        ticket_query(
            root=None,
            info=ghl_mock_info,
            id=ticket.pk,
        )


def test_not_found(ghl_auth_mock_info, ticket_query):
    """Test not found ticket retrieving."""
    with pytest.raises(GraphQLNotFound):
        ticket_query(
            root=None,
            info=ghl_auth_mock_info,
            id=1,
        )
