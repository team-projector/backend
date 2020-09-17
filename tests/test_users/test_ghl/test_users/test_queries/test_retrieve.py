# -*- coding: utf-8 -*-

import pytest
from jnt_django_graphene_toolbox.errors import GraphQLNotFound

GHL_QUERY_USER = """
query ($id: ID!) {
  user(id: $id) {
    id
    login
  }
}
"""


def test_query(user, ghl_client):
    """Test getting user raw query."""
    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_USER,
        variable_values={"id": user.id},
    )

    assert "errors" not in response
    assert response["data"]["user"]["id"] == str(user.id)


def test_success(user, ghl_auth_mock_info, user_query):
    """Test success user retrieving."""
    response = user_query(root=None, info=ghl_auth_mock_info, id=user.id)

    assert response == user


def test_inactive(user, ghl_auth_mock_info, user_query):
    """Test success inactive user retrieving."""
    user.is_active = False
    user.save(update_fields=["is_active"])

    with pytest.raises(GraphQLNotFound):
        user_query(
            root=None,
            info=ghl_auth_mock_info,
            id=user.id,
        )
