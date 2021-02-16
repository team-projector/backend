from tests.test_development.factories import IssueFactory
from tests.test_users.factories import UserFactory


def test_query_by_participated(user, gql_client_authenticated, gql_raw):
    """Test getting all issues by participated."""
    IssueFactory.create_batch(3, user=user)
    issues = IssueFactory.create_batch(4)
    for issue in issues:
        issue.participants.add(user, UserFactory.create())

    response = gql_client_authenticated.execute(
        gql_raw("all_issues"),
        variable_values={"participatedBy": user.pk},
    )

    assert "errors" not in response
    assert _all_issues_data(response)["count"] == 4

    issues_ids = [str(user_issue.pk) for user_issue in issues]

    for edge in _all_issues_data(response)["edges"]:
        assert edge["node"]["id"] in issues_ids


def test_created_by_for_other(user, gql_client_authenticated, gql_raw):
    """Test created_by_for_other from raw graphql."""
    issue = IssueFactory.create(author=user)
    IssueFactory.create_batch(2, user=user)

    response = gql_client_authenticated.execute(
        gql_raw("all_issues"),
        variable_values={"createdByForOther": user.pk},
    )

    assert "errors" not in response
    assert _all_issues_data(response)["count"] == 1

    edge = _all_issues_data(response)["edges"][0]
    assert edge["node"]["id"] == str(issue.pk)


def _all_issues_data(response):
    return response["data"]["allIssues"]
