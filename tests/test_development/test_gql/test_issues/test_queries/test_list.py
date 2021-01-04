import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models import TeamMember
from tests.test_development.factories import (
    IssueFactory,
    TeamFactory,
    TeamMemberFactory,
)
from tests.test_users.factories import UserFactory

ALL_ISSUES_QUERY = "all_issues"
ERRORS_FIELD = "errors"
COUNT_FIELD = "count"


def test_query(user, gql_client_authenticated, gql_raw):
    """Test getting all issues raw query."""
    IssueFactory.create_batch(5, user=user)

    response = gql_client_authenticated.execute(gql_raw(ALL_ISSUES_QUERY))

    assert ERRORS_FIELD not in response
    assert _all_issues_data(response)[COUNT_FIELD] == 5


def test_query_with_order_by(user, gql_client_authenticated, gql_raw):
    """Test getting all issues raw query with ordering."""
    IssueFactory.create_batch(5, user=user)

    response = gql_client_authenticated.execute(
        gql_raw(ALL_ISSUES_QUERY),
        variable_values={"orderBy": "due_date"},
    )

    assert ERRORS_FIELD not in response
    assert _all_issues_data(response)[COUNT_FIELD] == 5


def test_query_with_order_by_not_valid(
    user,
    gql_client_authenticated,
    gql_raw,
):
    """Test not valid ordering."""
    response = gql_client_authenticated.execute(
        gql_raw(ALL_ISSUES_QUERY),
        variable_values={"orderBy": "dueDate"},
    )

    assert not _all_issues_data(response)["count"]


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
    response = all_issues_query(
        root=None,
        info=ghl_mock_info,
    )

    assert isinstance(response, GraphQLPermissionDenied)


@pytest.mark.parametrize(
    ("roles", "count"),
    [
        (TeamMember.roles.WATCHER, 0),
        (TeamMember.roles.WATCHER | TeamMember.roles.DEVELOPER, 3),
        (TeamMember.roles.LEADER, 3),
    ],
)
def test_list_as_watcher_by_team(
    user,
    gql_client_authenticated,
    gql_raw,
    roles,
    count,
):
    """Test get issues as watcher from one team."""
    developer = UserFactory.create()
    IssueFactory.create_batch(3, user=developer)

    team = TeamFactory.create()

    TeamMemberFactory.create(
        team=team,
        user=user,
        roles=TeamMember.roles.WATCHER,
    )
    TeamMemberFactory.create(
        team=team,
        user=developer,
        roles=roles,
    )

    response = gql_client_authenticated.execute(
        gql_raw("all_issues"),
        variable_values={"team": team.pk},
    )

    assert ERRORS_FIELD not in response
    assert _all_issues_data(response)[COUNT_FIELD] == count


def _all_issues_data(response):
    return response["data"]["allIssues"]
