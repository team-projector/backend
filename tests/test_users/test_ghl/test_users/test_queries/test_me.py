from apps.users.models import User


def test_query(user, ghl_client, ghl_raw):
    """Test me raw query."""
    user.roles = User.roles.DEVELOPER | User.roles.MANAGER
    user.save()

    ghl_client.set_user(user)

    response = ghl_client.execute(ghl_raw("me"))

    assert response["data"]["me"]["id"] == str(user.id)
    assert response["data"]["me"]["roles"] == ["DEVELOPER", "MANAGER"]


def test_resolver(user, ghl_auth_mock_info, me_query):
    """Test me query."""
    response = me_query(root=None, info=ghl_auth_mock_info)

    assert response == user
