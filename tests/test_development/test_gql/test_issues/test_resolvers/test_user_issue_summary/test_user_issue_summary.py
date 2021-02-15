from apps.users.graphql.resolvers import resolve_user_issues_summary
from tests.test_development.test_gql.test_issues.test_resolvers.test_user_issue_summary.helpers import (  # noqa: E501
    assert_user_issue_summary,
)


def test_simple_resolver(
    user,
    ghl_auth_mock_info,
    issues_created_by,
    issues_assigned,
    issues_participation,
):
    """Test resolver not combined issues."""
    issues_summary = resolve_user_issues_summary(user, ghl_auth_mock_info)

    assert_user_issue_summary(user, issues_summary)


def test_resolver(
    user,
    ghl_auth_mock_info,
    issues_created_by,
    issues_assigned,
    issues_participation,
):
    """Test resolver."""
    issues_created_by[1].user = user
    issues_created_by[1].save()
    issues_created_by[1].participants.add(user)

    issues_assigned[2].author = user
    issues_assigned[2].save()

    issues_participation[1].author = user
    issues_participation[1].save()

    issues_participation[2].user = user
    issues_participation[2].save()

    issues_summary = resolve_user_issues_summary(user, ghl_auth_mock_info)

    assert_user_issue_summary(user, issues_summary)
