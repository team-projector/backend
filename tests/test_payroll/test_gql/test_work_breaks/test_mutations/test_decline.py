from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models import TeamMember
from apps.payroll.models.mixins.approved import ApprovedState
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories import UserFactory


def test_query(user, gql_client, gql_raw):
    """Test decline raw query."""
    gql_client.set_user(user)

    team = TeamFactory.create()
    user1 = UserFactory.create()

    TeamMemberFactory.create(
        team=team,
        user=user,
        roles=TeamMember.roles.LEADER,
    )
    TeamMemberFactory.create(
        team=team,
        user=user1,
        roles=TeamMember.roles.DEVELOPER,
    )
    work_break = WorkBreakFactory.create(user=user1)

    response = gql_client.execute(
        gql_raw("decline_work_break"),
        variable_values={"id": work_break.pk, "declineReason": "reason"},
    )

    work_break.refresh_from_db()

    assert response["data"]["declineWorkBreak"]["workBreak"]["id"] == (
        str(work_break.id)
    )
    assert work_break.approved_by == user
    assert work_break.decline_reason == "reason"
    assert work_break.approve_state == ApprovedState.DECLINED


def test_not_team_lead(ghl_auth_mock_info, decline_work_break_mutation):
    """
    Test not team lead.

    :param ghl_auth_mock_info:
    :param decline_work_break_mutation:
    """
    work_break = WorkBreakFactory.create()

    response = decline_work_break_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=work_break.pk,
    )

    assert isinstance(response, GraphQLPermissionDenied)

    work_break.refresh_from_db()

    assert not work_break.approved_by
    assert work_break.approve_state == ApprovedState.CREATED


def test_other_team_teamlead(  # noqa: WPS211
    user,
    ghl_auth_mock_info,
    team,
    make_team_developer,
    make_team_leader,
    decline_work_break_mutation,
):
    """
    Test other team teamlead.

    :param user:
    :param ghl_auth_mock_info:
    :param team:
    :param make_team_developer:
    :param make_team_leader:
    :param decline_work_break_mutation:
    """
    make_team_leader(team, user)

    another_team = TeamFactory.create()
    another_user = UserFactory.create()
    make_team_developer(another_team, another_user)

    work_break = WorkBreakFactory.create(user=another_user)

    response = decline_work_break_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=work_break.id,
    )
    assert isinstance(response, GraphQLPermissionDenied)


def test_owner(ghl_auth_mock_info, decline_work_break_mutation):
    """
    Test owner.

    :param ghl_auth_mock_info:
    :param decline_work_break_mutation:
    """
    work_break = WorkBreakFactory.create(user=ghl_auth_mock_info.context.user)

    response = decline_work_break_mutation(
        root=None,
        info=ghl_auth_mock_info,
        id=work_break.pk,
    )
    assert isinstance(response, GraphQLPermissionDenied)

    work_break.refresh_from_db()

    assert not work_break.approved_by
    assert work_break.approve_state == ApprovedState.CREATED
