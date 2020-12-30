from apps.development.models import TeamMember
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories import UserFactory


def test_query(user, gql_client_authenticated, gql_raw):
    """
    Test query.

    :param user:
    :param gql_client_authenticated:
    """
    SalaryFactory.create_batch(size=3, user=user)

    response = gql_client_authenticated.execute(gql_raw("all_salaries"))

    assert "errors" not in response
    assert response["data"]["allSalaries"]["count"] == 3


def test_unauth(ghl_mock_info, all_salaries_query):
    """
    Test unauth.

    :param ghl_mock_info:
    :param all_salaries_query:
    """
    response = all_salaries_query(
        root=None,
        info=ghl_mock_info,
    )
    assert not response.length


def test_not_allowed_for_user(user, all_salaries_query, ghl_auth_mock_info):
    """
    Test not allowed for user.

    :param user:
    :param all_salaries_query:
    :param ghl_auth_mock_info:
    """
    SalaryFactory.create_batch(size=2, user=UserFactory())
    response = all_salaries_query(root=None, info=ghl_auth_mock_info)

    assert response.length == 0


def test_allowed_to_leader(user, all_salaries_query, ghl_auth_mock_info):
    """
    Test allowed to leader.

    :param user:
    :param all_salaries_query:
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

    SalaryFactory.create_batch(size=2, user=developer)
    response = all_salaries_query(root=None, info=ghl_auth_mock_info)

    assert response.length == 2
