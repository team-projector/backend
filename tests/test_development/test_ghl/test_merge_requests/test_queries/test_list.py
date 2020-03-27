# -*- coding: utf-8 -*-

from django.db import connection
from django.test import override_settings

from apps.development.models import TeamMember
from tests.test_development.factories import (
    MergeRequestFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_users.factories.user import UserFactory

GHL_QUERY_ALL_MERGE_REQUESTS = """
query {
  allMergeRequests {
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

GHL_QUERY_ALL_MERGE_REQUESTS_WITH_USER = """
query {
  allMergeRequests {
    count
    edges {
      node {
        id
        title
        user {
          id
          roles
        }
      }
    }
  }
}
"""


def test_query(user, gql_client_authenticated):
    """Test getting merge requests via a raw query."""
    MergeRequestFactory.create_batch(2, user=user)

    response = gql_client_authenticated.execute(GHL_QUERY_ALL_MERGE_REQUESTS)

    assert "errors" not in response
    assert response["data"]["allMergeRequests"]["count"] == 2


def test_team_members_combined(
    user, all_merge_requests_query, ghl_auth_mock_info,
):
    """Test access by the leader role."""
    MergeRequestFactory.create_batch(2, user=user)

    user2 = UserFactory()
    MergeRequestFactory.create_batch(3, user=user2)

    team = TeamFactory()
    TeamMemberFactory(user=user, team=team, roles=TeamMember.roles.LEADER)
    TeamMemberFactory(user=user2, team=team, roles=TeamMember.roles.DEVELOPER)

    response = all_merge_requests_query(root=None, info=ghl_auth_mock_info)

    assert response.length == 5


def test_merge_requests_no_teamlead_or_owner(
    user, all_merge_requests_query, ghl_auth_mock_info,
):
    """Test no access."""
    MergeRequestFactory(user=UserFactory())

    response = all_merge_requests_query(root=None, info=ghl_auth_mock_info)

    assert response.length == 0


@override_settings(DEBUG=True)
def test_user_is_prefetched(
    user, gql_client_authenticated,
):
    """Test no n+1 for merge request users."""
    MergeRequestFactory(user=user)

    initial_q = len(connection.queries)
    gql_client_authenticated.execute(GHL_QUERY_ALL_MERGE_REQUESTS)
    response_q = len(connection.queries) - initial_q

    gql_client_authenticated.execute(GHL_QUERY_ALL_MERGE_REQUESTS_WITH_USER)

    assert len(connection.queries) == initial_q + response_q * 2
