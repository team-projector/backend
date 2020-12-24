from apps.users.models import User


def test_query(user, gql_client, gql_raw):
    """Test me raw query."""
    user.roles = User.roles.DEVELOPER | User.roles.MANAGER
    user.save()

    gql_client.set_user(user)

    response = gql_client.execute(gql_raw("me"))

    assert response["data"]["me"]["id"] == str(user.id)
    assert response["data"]["me"]["roles"] == ["DEVELOPER", "MANAGER"]


def test_resolver(user, ghl_auth_mock_info, me_query):
    """Test me query."""
    response = me_query(root=None, info=ghl_auth_mock_info)

    assert response == user
