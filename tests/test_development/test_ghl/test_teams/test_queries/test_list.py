# -*- coding: utf-8 -*-

from pytest import raises

from apps.core.graphql.errors import GraphQLPermissionDenied
from tests.test_development.factories import TeamFactory
from tests.test_users.factories import UserFactory

GHL_QUERY_ALL_TEAMS = """
{
  allTeams {
    count
    edges {
      node {
        id
        title
      }
    }
  }
}
"""


def test_query(user, gql_client_authenticated):
    """Test getting all teams raw query."""
    TeamFactory.create_batch(5, members=[user])

    response = gql_client_authenticated.execute(
        GHL_QUERY_ALL_TEAMS,
    )

    assert response["data"]["allTeams"]["count"] == 5


def test_not_team_member(user, ghl_auth_mock_info, all_teams_query):
    """Test no teams if user no team member."""
    TeamFactory.create_batch(5, members=[UserFactory.create()])

    response = all_teams_query(
        root=None,
        info=ghl_auth_mock_info,
    )

    assert not response.length


def test_unauth(user, ghl_mock_info, all_teams_query):
    """Test not auth query."""
    with raises(GraphQLPermissionDenied):
        all_teams_query(
            root=None,
            info=ghl_mock_info,
        )


def test_some_teams(user, ghl_auth_mock_info, all_teams_query):
    teams = TeamFactory.create_batch(2, members=[user])
    TeamFactory.create_batch(2)

    response = all_teams_query(
        root=None,
        info=ghl_auth_mock_info,
    )

    assert response.length == 2
    assert response.edges[0].node in teams
    assert response.edges[1].node in teams
