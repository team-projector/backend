from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from tests.test_development.factories import TicketFactory


def test_query(user, gql_client, gql_raw):
    """Test getting ticket raw query."""
    ticket = TicketFactory.create()

    gql_client.set_user(user)

    response = gql_client.execute(
        gql_raw("ticket"),
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

    response = ticket_query(
        root=None,
        info=ghl_mock_info,
        id=ticket.pk,
    )
    assert isinstance(response, GraphQLPermissionDenied)


def test_not_found(ghl_auth_mock_info, ticket_query):
    """Test not found ticket retrieving."""
    response = ticket_query(
        root=None,
        info=ghl_auth_mock_info,
        id=1,
    )
    assert response is None
