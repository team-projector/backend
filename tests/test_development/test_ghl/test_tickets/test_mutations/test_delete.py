# -*- coding: utf-8 -*-

from pytest import raises

from apps.core.graphql.errors import GraphQLPermissionDenied

GHL_DELETE_TICKET = """
mutation ($id: ID!) {
  deleteTicket (id: $id) {
    ok
  }
}
"""


def test_query(project_manager, ghl_client, ticket):
    """Test delete ticket raw query."""
    ghl_client.set_user(project_manager)

    response = ghl_client.execute(
        GHL_DELETE_TICKET,
        variables={
            'id': ticket.pk,
        },
    )

    assert 'errors' not in response
    assert response['data']['deleteTicket']['ok']


def test_success(
    project_manager,
    ghl_auth_mock_info,
    delete_ticket_mutation,
    ticket,
):
    """Test success ticket delete."""
    response = delete_ticket_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=ticket.pk,
    )

    assert response.ok


def test_unauth(ghl_mock_info, delete_ticket_mutation):
    """Test unauth ticket deleting."""
    with raises(GraphQLPermissionDenied):
        delete_ticket_mutation(
            root=None,
            info=ghl_mock_info,
        )


def test_not_project_manager(ghl_auth_mock_info, delete_ticket_mutation):
    """Test not project manager ticket deleting."""
    with raises(GraphQLPermissionDenied):
        delete_ticket_mutation(
            root=None,
            info=ghl_auth_mock_info,
            id=1,
        )
