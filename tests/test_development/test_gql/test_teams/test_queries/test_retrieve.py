from tests.test_development.factories import TeamFactory
from tests.test_users.factories import UserFactory

TEAM_QUERY = "team"
KEY_ID = "id"
KEY_TEAM = "team"


def test_query(user, gql_client, gql_raw):
    """Test retrieve team raw query."""
    team = TeamFactory.create(members=[user])

    gql_client.set_user(user)

    response = gql_client.execute(
        gql_raw(TEAM_QUERY),
        variable_values={KEY_ID: team.pk},
    )

    assert "errors" not in response
    assert response["data"][KEY_TEAM][KEY_ID] == str(team.pk)


def test_query_not_found(user, gql_client, gql_raw):
    """Test retrieve team raw query."""
    team = TeamFactory.create(members=[user])

    gql_client.set_user(user)

    response = gql_client.execute(
        gql_raw(TEAM_QUERY),
        variable_values={KEY_ID: team.pk + 1},
    )

    assert response["data"][KEY_TEAM] is None


def test_unauth(ghl_mock_info, team_query):
    """Test unauth team retrieving."""
    response = team_query(
        root=None,
        info=ghl_mock_info,
        id=1,
    )

    assert response is None


def test_not_found(ghl_auth_mock_info, team_query):
    """Test not found team retrieving."""
    response = team_query(
        root=None,
        info=ghl_auth_mock_info,
        id=1,
    )

    assert response is None


def test_not_member(user, ghl_auth_mock_info, team_query):
    """
    Test not member.

    :param user:
    :param ghl_auth_mock_info:
    :param team_query:
    """
    response = team_query(
        root=None,
        info=ghl_auth_mock_info,
        id=TeamFactory.create().pk,
    )

    assert response is None


def test_get_team_with_members(user, gql_client, gql_raw):
    """Test retrieve team with members, filter inactive."""
    inactive_user = UserFactory.create(is_active=False)
    team = TeamFactory.create(members=[user, inactive_user])

    gql_client.set_user(user)

    response = gql_client.execute(
        gql_raw("team_with_members"),
        variable_values={KEY_ID: team.pk},
    )

    assert "errors" not in response
    members = response["data"][KEY_TEAM]["members"]
    assert members["count"] == 1
    node = members["edges"][0]["node"]
    assert node["user"][KEY_ID] == str(user.pk)
