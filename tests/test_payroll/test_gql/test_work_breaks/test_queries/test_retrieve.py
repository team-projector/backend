from apps.development.models import TeamMember
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories import UserFactory


def test_query(user, gql_client, gql_raw):
    """Test raw query."""
    gql_client.set_user(user)

    work_break = WorkBreakFactory.create(user=user)

    response = gql_client.execute(
        gql_raw("work_break"),
        variable_values={"id": work_break.pk},
    )

    assert response["data"]["workBreak"]["id"] == str(work_break.id)


def test_not_team_lead(ghl_auth_mock_info, work_break_query):
    """
    Test not team lead.

    :param ghl_auth_mock_info:
    :param work_break_query:
    """
    work_break = WorkBreakFactory.create()

    response = work_break_query(
        root=None,
        info=ghl_auth_mock_info,
        id=work_break.pk,
    )

    assert response is None


def test_as_team_lead(ghl_auth_mock_info, work_break_query):
    """
    Test as team lead.

    :param ghl_auth_mock_info:
    :param work_break_query:
    """
    team = TeamFactory.create()
    user = UserFactory.create()

    TeamMemberFactory.create(
        team=team,
        user=ghl_auth_mock_info.context.user,
        roles=TeamMember.roles.LEADER,
    )
    TeamMemberFactory.create(
        team=team,
        user=user,
        roles=TeamMember.roles.DEVELOPER,
    )
    work_break = WorkBreakFactory.create(user=user)

    work_break_node = work_break_query(
        root=None,
        info=ghl_auth_mock_info,
        id=work_break.pk,
    )

    assert work_break_node.id == work_break.id
    assert work_break_node.user != ghl_auth_mock_info.context.user
