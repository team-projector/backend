import pytest
from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from apps.development.models import TeamMember
from apps.payroll.graphql.fields.work_breaks import WorkBreakFilterSet
from apps.payroll.models import WorkBreak
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories.user import UserFactory


def test_filter_by_team(
    user,
    team,
    ghl_auth_mock_info,
    team_developer,
    team_leader,
):
    """
    Test filter by team.

    :param user:
    :param team:
    :param ghl_auth_mock_info:
    :param team_developer:
    :param team_leader:
    """
    work_breaks = WorkBreakFactory.create_batch(size=5, user=team_developer)
    WorkBreakFactory.create_batch(size=5, user=UserFactory.create())

    TeamMember.objects.filter(user=user, team=team).update(
        roles=TeamMember.roles.LEADER,
    )

    ghl_auth_mock_info.context.user = team_leader

    queryset = WorkBreakFilterSet(
        data={"team": team.pk},
        queryset=WorkBreak.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert queryset.count() == 5
    assert set(queryset) == set(work_breaks)


def test_filter_by_team_not_allowed(
    user,
    ghl_auth_mock_info,
    team,
    make_team_developer,
    team_developer,
):
    """
    Test filter by team not allowed.

    :param user:
    :param ghl_auth_mock_info:
    :param team:
    :param make_team_developer:
    :param team_developer:
    """
    make_team_developer(team, user)
    WorkBreakFactory.create_batch(size=5, user=team_developer)

    with pytest.raises(GraphQLPermissionDenied):
        WorkBreakFilterSet(  # noqa: WPS428
            data={"team": team.id},
            queryset=WorkBreak.objects.all(),
            request=ghl_auth_mock_info.context,
        ).qs
