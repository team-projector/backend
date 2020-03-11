# -*- coding: utf-8 -*-

import pytest

from apps.core.graphql.errors import GraphQLNotFound, GraphQLPermissionDenied
from tests.test_development.factories import IssueFactory

GHL_QUERY_ISSUE = """
query ($id: ID!) {
  issue (id: $id) {
    id
    title
  }
}
"""


def test_query(user, ghl_client):
    """Test getting issue raw query."""
    issue = IssueFactory(user=user)

    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_ISSUE,
        variable_values={
            "id": issue.pk,
        },
    )

    assert "errors" not in response
    assert response["data"]["issue"]["id"] == str(issue.pk)


def test_unauth(db, ghl_mock_info, issue_query):
    """Test unauth issue retrieving."""
    issue = IssueFactory()

    with pytest.raises(GraphQLPermissionDenied):
        issue_query(
            root=None,
            info=ghl_mock_info,
            id=issue.pk,
        )


def test_not_found(ghl_auth_mock_info, issue_query):
    """Test not found issue retrieving."""
    with pytest.raises(GraphQLNotFound):
        issue_query(
            root=None,
            info=ghl_auth_mock_info,
            id=1,
        )
