from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.users.models import User

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
        variable_values={"id": ticket.pk},
    )

    assert "errors" not in response
    assert response["data"]["deleteTicket"]["ok"]


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
    resolve = delete_ticket_mutation(root=None, info=ghl_mock_info)

    assert isinstance(resolve, GraphQLPermissionDenied)


def test_not_project_manager(user, ghl_auth_mock_info, delete_ticket_mutation):
    """Test not project manager ticket deleting."""
    user.roles = User.roles.DEVELOPER
    user.save()
    resolve = delete_ticket_mutation(root=None, info=ghl_auth_mock_info, id=1)

    assert isinstance(resolve, GraphQLPermissionDenied)
