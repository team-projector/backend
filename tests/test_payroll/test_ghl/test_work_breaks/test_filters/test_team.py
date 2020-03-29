# -*- coding: utf-8 -*-

import pytest

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.development.models import TeamMember
from apps.payroll.graphql.filters import WorkBreakFilterSet
from apps.payroll.models import WorkBreak
from tests.test_payroll.factories import WorkBreakFactory
from tests.test_users.factories.user import UserFactory


def test_filter_by_team(
    user, team, ghl_auth_mock_info, team_developer, team_leader,
):
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
    user, ghl_auth_mock_info, team, make_team_developer, team_developer,
):
    make_team_developer(team, user)
    WorkBreakFactory.create_batch(size=5, user=team_developer)

    with pytest.raises(GraphQLPermissionDenied):
        WorkBreakFilterSet(  # noqa: WPS428
            data={"team": team.id},
            queryset=WorkBreak.objects.all(),
            request=ghl_auth_mock_info.context,
        ).qs
