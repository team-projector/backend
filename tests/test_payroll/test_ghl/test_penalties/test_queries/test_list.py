# -*- coding: utf-8 -*-

import pytest

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.development.models import TeamMember
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import PenaltyFactory
from tests.test_users.factories import UserFactory

GHL_QUERY_ALL_PENALTIES = """
query {
  allPenalties {
    count
    edges {
      node {
        id
        sum
        comment
      }
    }
  }
}
"""


def test_query(user, gql_client_authenticated):
    PenaltyFactory.create_batch(size=3, user=user)

    response = gql_client_authenticated.execute(
        GHL_QUERY_ALL_PENALTIES,
    )

    assert "errors" not in response
    assert response["data"]["allPenalties"]["count"] == 3


def test_unauth(ghl_mock_info, all_penalties_query):
    with pytest.raises(GraphQLPermissionDenied):
        all_penalties_query(
            root=None,
            info=ghl_mock_info,
        )


def test_not_allowed_for_user(user, all_penalties_query, ghl_auth_mock_info):
    PenaltyFactory.create_batch(size=2, user=UserFactory())
    response = all_penalties_query(
        root=None,
        info=ghl_auth_mock_info,
    )

    assert response.length == 0


def test_allowed_to_leader(user, all_penalties_query, ghl_auth_mock_info):
    team = TeamFactory()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER
    )

    developer = UserFactory()
    TeamMemberFactory.create(
        user=developer,
        team=team,
        roles=TeamMember.roles.DEVELOPER
    )

    PenaltyFactory.create_batch(size=2, user=developer)
    response = all_penalties_query(
        root=None,
        info=ghl_auth_mock_info,
    )

    assert response.length == 2
