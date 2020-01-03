# -*- coding: utf-8 -*-

from pytest import raises

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.users.models import Token

GHL_QUERY_LOGOUT = """
mutation {
    logout {
        status
    }
}
"""


def test_query(user, ghl_client):
    """Test logout raw query."""
    ghl_client.set_user(user)

    assert Token.objects.filter(user=user).exists()

    response = ghl_client.execute(GHL_QUERY_LOGOUT)

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
    with raises(GraphQLPermissionDenied):
        logout_mutation(root=None, info=ghl_mock_info)
