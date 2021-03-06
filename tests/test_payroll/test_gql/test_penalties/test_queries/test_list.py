from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models import TeamMember
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import PenaltyFactory
from tests.test_users.factories import UserFactory


def test_query(user, gql_client_authenticated, gql_raw):
    """
    Test query.

    :param user:
    :param gql_client_authenticated:
    """
    PenaltyFactory.create_batch(size=3, user=user)

    response = gql_client_authenticated.execute(gql_raw("all_penalties"))

    assert "errors" not in response
    assert response["data"]["allPenalties"]["count"] == 3


def test_unauth(ghl_mock_info, all_penalties_query):
    """
    Test unauth.

    :param ghl_mock_info:
    :param all_penalties_query:
    """
    response = all_penalties_query(
        root=None,
        info=ghl_mock_info,
    )

    assert isinstance(response, GraphQLPermissionDenied)


def test_not_allowed_for_user(user, all_penalties_query, ghl_auth_mock_info):
    """
    Test not allowed for user.

    :param user:
    :param all_penalties_query:
    :param ghl_auth_mock_info:
    """
    PenaltyFactory.create_batch(size=2, user=UserFactory.create())
    response = all_penalties_query(root=None, info=ghl_auth_mock_info)

    assert response.length == 0


def test_allowed_to_leader(user, all_penalties_query, ghl_auth_mock_info):
    """
    Test allowed to leader.

    :param user:
    :param all_penalties_query:
    :param ghl_auth_mock_info:
    """
    team = TeamFactory()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER,
    )

    developer = UserFactory()
    TeamMemberFactory.create(
        user=developer,
        team=team,
        roles=TeamMember.roles.DEVELOPER,
    )

    PenaltyFactory.create_batch(size=2, user=developer)
    response = all_penalties_query(root=None, info=ghl_auth_mock_info)

    assert response.length == 2
