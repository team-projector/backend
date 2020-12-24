from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.users.models import Token


def test_query(user, gql_client, ghl_raw):
    """Test logout raw query."""
    gql_client.set_user(user)

    assert Token.objects.filter(user=user).exists()

    response = gql_client.execute(ghl_raw("logout"))

    assert "errors" not in response
    assert response["data"]["logout"]["status"] == "success"
    assert not Token.objects.filter(user=user).exists()


def test_success(user, ghl_auth_mock_info, logout_mutation):
    """Test success logout."""
    assert Token.objects.filter(user=user).exists()

    logout_mutation(root=None, info=ghl_auth_mock_info)

    assert not Token.objects.filter(user=user).exists()


def test_non_auth(user, ghl_mock_info, logout_mutation):
    """Test logout if user is not logged."""
    response = logout_mutation(root=None, info=ghl_mock_info)
    assert isinstance(response, GraphQLPermissionDenied)
