import pytest
from jnt_django_graphene_toolbox.errors import (
    GraphQLNotFound,
    GraphQLPermissionDenied,
)

from tests.test_development.factories import TeamFactory
from tests.test_users.factories import UserFactory

TEAM_QUERY = "team"
KEY_ID = "id"


def test_query(user, ghl_client, ghl_raw):
    """Test retrieve team raw query."""
    team = TeamFactory.create(members=[user])

    ghl_client.set_user(user)

    response = ghl_client.execute(
        ghl_raw(TEAM_QUERY),
        variable_values={KEY_ID: team.pk},
    )

    assert "errors" not in response
    assert response["data"]["team"][KEY_ID] == str(team.pk)


def test_query_found(user, ghl_client, ghl_raw):
    """Test retrieve team raw query."""
    team = TeamFactory.create(members=[user])

    ghl_client.set_user(user)

    response = ghl_client.execute(
        ghl_raw(TEAM_QUERY),
        variable_values={KEY_ID: team.pk + 1},
    )

    assert "errors" in response


def test_unauth(ghl_mock_info, team_query):
    """Test unauth team retrieving."""
    with pytest.raises(GraphQLPermissionDenied):
        team_query(
            root=None,
            info=ghl_mock_info,
            id=1,
        )


def test_not_found(ghl_auth_mock_info, team_query):
    """Test not found team retrieving."""
    with pytest.raises(GraphQLNotFound):
        team_query(
            root=None,
            info=ghl_auth_mock_info,
            id=1,
        )


def test_not_member(user, ghl_auth_mock_info, team_query):
    """
    Test not member.

    :param user:
    :param ghl_auth_mock_info:
    :param team_query:
    """
    with pytest.raises(GraphQLNotFound):
        team_query(
            root=None,
            info=ghl_auth_mock_info,
            id=TeamFactory.create().pk,
        )


def test_get_team_with_members(user, ghl_client, ghl_raw):
    """Test retrieve team with members, filter inactive."""
    inactive_user = UserFactory.create(is_active=False)
    team = TeamFactory.create(members=[user, inactive_user])

    ghl_client.set_user(user)

    response = ghl_client.execute(
        ghl_raw("team_with_members"),
        variable_values={KEY_ID: team.pk},
    )

    assert "errors" not in response
    members = response["data"]["team"]["members"]
    assert members["count"] == 1
    node = members["edges"][0]["node"]
    assert node["user"][KEY_ID] == str(user.pk)
