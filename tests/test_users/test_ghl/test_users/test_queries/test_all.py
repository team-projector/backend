import pytest

from tests.test_users.factories import UserFactory


@pytest.fixture()
def raw_query(assets):
    """Getting raw query from disk."""
    return assets.open_file("all_users.ghl", "r").read()


def test_raw_query(user, ghl_client, raw_query):
    """Test getting all users raw query."""
    ghl_client.set_user(user)

    response = ghl_client.execute(raw_query)

    assert "errors" not in response
    assert response["data"]["users"]["count"] == 1


def test_success(user, ghl_auth_mock_info, all_users_query):
    """Test success getting users."""
    UserFactory.create(is_active=False)

    response = all_users_query(root=None, info=ghl_auth_mock_info)

    assert len(response.edges) == 1
    assert response.edges[0].node == user
