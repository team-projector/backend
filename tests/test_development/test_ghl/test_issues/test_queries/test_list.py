# -*- coding: utf-8 -*-

from pytest import raises

from apps.core.graphql.errors import GraphQLPermissionDenied
from tests.test_development.factories import IssueFactory

GHL_QUERY_ALL_ISSUES = """
query {
  allIssues {
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
    """Test getting all issues raw query."""
    IssueFactory.create_batch(5, user=user)

    response = gql_client_authenticated.execute(
        GHL_QUERY_ALL_ISSUES,
    )

    assert 'errors' not in response
    assert response['data']['allIssues']['count'] == 5


def test_not_owned_issue(ghl_auth_mock_info, all_issues_query):
    IssueFactory()
    response = all_issues_query(
        root=None,
        info=ghl_auth_mock_info,
    )

    assert response.length == 0


def test_unauth(ghl_mock_info, all_issues_query):
    """Test unauth issues list."""
    with raises(GraphQLPermissionDenied):
        all_issues_query(
            root=None,
            info=ghl_mock_info,
        )
