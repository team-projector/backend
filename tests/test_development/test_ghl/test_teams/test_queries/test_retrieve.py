# -*- coding: utf-8 -*-

import pytest
from jnt_django_graphene_toolbox.errors import (
    GraphQLNotFound,
    GraphQLPermissionDenied,
)

from tests.test_development.factories import TeamFactory

GHL_QUERY_TEAM = """
query ($id: ID!) {
  team(id: $id) {
    id
    title
  }
}
"""


def test_query(user, ghl_client):
    """Test retrieve team raw query."""
    team = TeamFactory.create(members=[user])

    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_TEAM, variable_values={"id": team.pk},
    )

    assert "errors" not in response
    assert response["data"]["team"]["id"] == str(team.pk)


def test_query_found(user, ghl_client):
    """Test retrieve team raw query."""
    team = TeamFactory.create(members=[user])

    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_TEAM, variable_values={"id": team.pk + 1},
    )

    assert "errors" in response


def test_unauth(ghl_mock_info, team_query):
    """Test unauth team retrieving."""
    with pytest.raises(GraphQLPermissionDenied):
        team_query(
            root=None, info=ghl_mock_info, id=1,
        )


def test_not_found(ghl_auth_mock_info, team_query):
    """Test not found team retrieving."""
    with pytest.raises(GraphQLNotFound):
        team_query(
            root=None, info=ghl_auth_mock_info, id=1,
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
            root=None, info=ghl_auth_mock_info, id=TeamFactory.create().pk,
        )
