# -*- coding: utf-8 -*-

from apps.development.graphql.filters import TeamsFilterSet
from apps.development.models import Team, TeamMember
from tests.helpers import lists
from tests.test_development.factories import TeamFactory, TeamMemberFactory


def test_filter_by_role(user, ghl_auth_mock_info, make_team_leader):
    TeamFactory.create_batch(5)
    team = TeamFactory.create()

    make_team_leader(team, user)

    results = TeamsFilterSet(
        data={"roles": "DEVELOPER"},
        queryset=Team.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert results.count() == 0

    results = TeamsFilterSet(
        data={"roles": "LEADER"},
        queryset=Team.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert results.count() == 1
    assert results.first() == team


def test_filter_many_roles(user, ghl_auth_mock_info):
    TeamFactory.create_batch(5)
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER | TeamMember.roles.DEVELOPER,
    )

    results = TeamsFilterSet(
        data={"roles": "LEADER"},
        queryset=Team.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert results.count() == 1
    assert results.first() == team

    results = TeamsFilterSet(
        data={"roles": "DEVELOPER"},
        queryset=Team.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert results.first() == team

    results = TeamsFilterSet(
        data={"roles": "WATCHER"},
        queryset=Team.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert results.count() == 0


def test_filter_by_user_and_many_roles(user, ghl_auth_mock_info):
    TeamFactory.create_batch(5)
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER | TeamMember.roles.DEVELOPER,
    )

    results = TeamsFilterSet(
        data={"roles": "LEADER,WATCHER"},
        queryset=Team.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert results.count() == 1
    assert results.first() == team


def test_search(user, make_team_leader):
    teams = [
        TeamFactory.create(title="create"),
        TeamFactory.create(title="react"),
        TeamFactory.create(title="test0"),
    ]

    make_team_leader(teams[0], user)
    make_team_leader(teams[1], user)
    make_team_leader(teams[2], user)

    results = TeamsFilterSet(data={"q": "ate"}, queryset=Team.objects.all()).qs

    assert results.count() == 1
    assert results.first() == teams[0]

    results = TeamsFilterSet(
        data={"q": "rea"}, queryset=Team.objects.all(),
    ).qs

    assert results.count() == 2
    assert set(results) == {teams[0], teams[1]}

    results = TeamsFilterSet(
        data={"q": "012345"}, queryset=Team.objects.all()
    ).qs

    assert results.count() == 0


def test_order_by_title(user, make_team_leader):
    teams = [
        TeamFactory.create(title="agent"),
        TeamFactory.create(title="cloud"),
        TeamFactory.create(title="bar"),
    ]

    make_team_leader(teams[0], user)
    make_team_leader(teams[1], user)
    make_team_leader(teams[2], user)

    results = TeamsFilterSet(
        data={"order_by": "title"}, queryset=Team.objects.all()
    ).qs

    assert list(results) == lists.sub_list(teams, (0, 2, 1))

    results = TeamsFilterSet(
        data={"order_by": "-title"}, queryset=Team.objects.all()
    ).qs

    assert list(results) == lists.sub_list(teams, (1, 2, 0))
