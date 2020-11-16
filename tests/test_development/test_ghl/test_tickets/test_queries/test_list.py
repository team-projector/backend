import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from tests.test_development.factories import TicketFactory


def test_query(user, ghl_client, ghl_raw):
    """Test getting all tickets raw query."""
    TicketFactory.create_batch(5)

    ghl_client.set_user(user)

    response = ghl_client.execute(ghl_raw("all_tickets"))

    assert "errors" not in response
    assert response["data"]["allTickets"]["count"] == 5


def test_success(ghl_auth_mock_info, all_tickets_query):
    """Test success tickets list."""
    TicketFactory.create_batch(5)

    response = all_tickets_query(root=None, info=ghl_auth_mock_info)

    assert response.length == 5


def test_unauth(ghl_mock_info, all_tickets_query):
    """Test unauth tickets list."""
    with pytest.raises(GraphQLPermissionDenied):
        all_tickets_query(
            root=None,
            info=ghl_mock_info,
        )
