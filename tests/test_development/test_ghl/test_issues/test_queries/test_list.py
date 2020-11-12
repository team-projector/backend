import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from tests.test_development.factories import IssueFactory


def test_query(user, gql_client_authenticated, ghl_raw):
    """Test getting all issues raw query."""
    IssueFactory.create_batch(5, user=user)

    response = gql_client_authenticated.execute(ghl_raw("all_issues"))

    assert "errors" not in response
    assert response["data"]["allIssues"]["count"] == 5


def test_not_owned_issue(ghl_auth_mock_info, all_issues_query):
    """
    Test not owned issue.

    :param ghl_auth_mock_info:
    :param all_issues_query:
    """
    IssueFactory()
    response = all_issues_query(root=None, info=ghl_auth_mock_info)

    assert response.length == 0


def test_unauth(ghl_mock_info, all_issues_query):
    """Test unauth issues list."""
    with pytest.raises(GraphQLPermissionDenied):
        all_issues_query(
            root=None,
            info=ghl_mock_info,
        )
