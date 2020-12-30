from apps.payroll.graphql.fields.all_work_breaks import AllWorkBreakFilterSet
from apps.payroll.models import WorkBreak
from apps.payroll.models.mixins.approved import ApprovedState
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories.user import UserFactory


def test_approving_list(
    user,
    ghl_auth_mock_info,
    team,
    make_team_leader,
    team_developer,
):
    """
    Test approving list.

    :param user:
    :param ghl_auth_mock_info:
    :param team:
    :param make_team_leader:
    :param team_developer:
    """
    make_team_leader(team, user)

    WorkBreakFactory.create_batch(5, user=team_developer)
    WorkBreakFactory.create_batch(
        4,
        user=team_developer,
        approve_state=ApprovedState.APPROVED,
    )
    WorkBreakFactory.create_batch(3, user=UserFactory.create())

    queryset = AllWorkBreakFilterSet(
        data={"approving": True},
        queryset=WorkBreak.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert queryset.count() == 5

    queryset = AllWorkBreakFilterSet(
        data={"approving": False},
        queryset=WorkBreak.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert queryset.count() == 12


def test_approving_list_not_teamlead(
    user,
    ghl_auth_mock_info,
    team,
    make_team_developer,
    team_developer,
):
    """
    Test approving list not teamlead.

    :param user:
    :param ghl_auth_mock_info:
    :param team:
    :param make_team_developer:
    :param team_developer:
    """
    make_team_developer(team, user)

    WorkBreakFactory.create_batch(5, user=user)
    WorkBreakFactory.create_batch(5, user=team_developer)
    WorkBreakFactory.create_batch(
        4,
        user=team_developer,
        approve_state=ApprovedState.APPROVED,
    )
    WorkBreakFactory.create_batch(3, user=UserFactory.create())

    queryset = AllWorkBreakFilterSet(
        data={"approving": True},
        queryset=WorkBreak.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert queryset.count() == 0
