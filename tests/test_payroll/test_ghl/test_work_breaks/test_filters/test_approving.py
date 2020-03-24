# -*- coding: utf-8 -*-

from apps.payroll.graphql.filters import WorkBreakFilterSet
from apps.payroll.models import WorkBreak
from apps.payroll.models.mixins.approved import ApprovedState
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories.user import UserFactory


def test_approving_list(
    user, ghl_auth_mock_info, team, make_team_leader, team_developer,
):
    make_team_leader(team, user)

    WorkBreakFactory.create_batch(5, user=team_developer)
    WorkBreakFactory.create_batch(
        4, user=team_developer, approve_state=ApprovedState.APPROVED,
    )
    WorkBreakFactory.create_batch(3, user=UserFactory.create())

    results = WorkBreakFilterSet(
        data={"approving": True},
        queryset=WorkBreak.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert results.count() == 5

    results = WorkBreakFilterSet(
        data={"approving": False},
        queryset=WorkBreak.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert results.count() == 12


def test_approving_list_not_teamlead(
    user, ghl_auth_mock_info, team, make_team_developer, team_developer,
):
    make_team_developer(team, user)

    WorkBreakFactory.create_batch(5, user=user)
    WorkBreakFactory.create_batch(5, user=team_developer)
    WorkBreakFactory.create_batch(
        4, user=team_developer, approve_state=ApprovedState.APPROVED,
    )
    WorkBreakFactory.create_batch(3, user=UserFactory.create())

    results = WorkBreakFilterSet(
        data={"approving": True},
        queryset=WorkBreak.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert results.count() == 0
