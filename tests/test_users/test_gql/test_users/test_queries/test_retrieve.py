import pytest
from jnt_django_graphene_toolbox.errors import GraphQLNotFound


def test_query(user, gql_client, gql_raw):
    """Test getting user raw query."""
    gql_client.set_user(user)

    response = gql_client.execute(
        gql_raw("user"),
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
