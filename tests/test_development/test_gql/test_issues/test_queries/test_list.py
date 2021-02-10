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
        variable_values={"orderBy": ["DUE_DATE_ASC"]},
    )

    assert ERRORS_FIELD not in response
    assert _all_issues_data(response)[COUNT_FIELD] == 5


def test_query_with_not_filter_args(user, gql_client_authenticated, gql_raw):
    """Test getting all issues raw query with non filter args."""
    IssueFactory.create_batch(5, user=user)

    response = gql_client_authenticated.execute(
        gql_raw(ALL_ISSUES_QUERY),
        variable_values={"offset": 2},
    )

    assert ERRORS_FIELD not in response
    assert len(_all_issues_data(response)["edges"]) == 3


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


def test_query_by_participiant(user, gql_client_authenticated, gql_raw):
    """Test getting all issues by participiant."""
    IssueFactory.create_batch(3, user=user)
    issues = IssueFactory.create_batch(4)
    for issue in issues:
        issue.participants.add(user, UserFactory.create())

    response = gql_client_authenticated.execute(
        gql_raw(ALL_ISSUES_QUERY),
        variable_values={"participatedBy": user.pk},
    )

    assert ERRORS_FIELD not in response
    assert _all_issues_data(response)[COUNT_FIELD] == 4

    issues_ids = [str(issue.pk) for issue in issues]

    for edge in _all_issues_data(response)["edges"]:
        assert edge["node"]["id"] in issues_ids


def _all_issues_data(response):
    return response["data"]["allIssues"]
