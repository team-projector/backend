# -*- coding: utf-8 -*-

from apps.development.graphql.filters import TeamsFilterSet
from apps.development.models import Team, TeamMember
from tests.helpers import lists
from tests.test_development.factories import TeamFactory, TeamMemberFactory


def test_filter_by_role(user, ghl_auth_mock_info, make_team_leader):
    """
    Test filter by role.

    :param user:
    :param ghl_auth_mock_info:
    :param make_team_leader:
    """
    TeamFactory.create_batch(5)
    team = TeamFactory.create()

    make_team_leader(team, user)

    queryset = TeamsFilterSet(
        data={"roles": "DEVELOPER"},
        queryset=Team.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert queryset.count() == 0

    queryset = TeamsFilterSet(
        data={"roles": "LEADER"},
        queryset=Team.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert queryset.count() == 1
    assert queryset.first() == team


def test_filter_many_roles(user, ghl_auth_mock_info):
    """
    Test filter many roles.

    :param user:
    :param ghl_auth_mock_info:
    """
    TeamFactory.create_batch(5)
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER | TeamMember.roles.DEVELOPER,
    )

    queryset = TeamsFilterSet(
        data={"roles": "LEADER"},
        queryset=Team.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert queryset.count() == 1
    assert queryset.first() == team

    queryset = TeamsFilterSet(
        data={"roles": "DEVELOPER"},
        queryset=Team.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert queryset.first() == team

    queryset = TeamsFilterSet(
        data={"roles": "WATCHER"},
        queryset=Team.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert queryset.count() == 0


def test_filter_by_user_and_many_roles(user, ghl_auth_mock_info):
    """
    Test filter by user and many roles.

    :param user:
    :param ghl_auth_mock_info:
    """
    TeamFactory.create_batch(5)
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER | TeamMember.roles.DEVELOPER,
    )

    queryset = TeamsFilterSet(
        data={"roles": "LEADER,WATCHER"},
        queryset=Team.objects.all(),
        request=ghl_auth_mock_info.context,
    ).qs

    assert queryset.count() == 1
    assert queryset.first() == team


def test_search(user, make_team_leader):
    """
    Test search.

    :param user:
    :param make_team_leader:
    """
    teams = [
        TeamFactory.create(title="create"),
        TeamFactory.create(title="react"),
        TeamFactory.create(title="test0"),
    ]

    make_team_leader(teams[0], user)
    make_team_leader(teams[1], user)
    make_team_leader(teams[2], user)

    queryset = TeamsFilterSet(
        data={"q": "ate"}, queryset=Team.objects.all(),
    ).qs

    assert queryset.count() == 1
    assert queryset.first() == teams[0]

    queryset = TeamsFilterSet(
        data={"q": "rea"}, queryset=Team.objects.all(),
    ).qs

    assert queryset.count() == 2
    assert set(queryset) == {teams[0], teams[1]}

    queryset = TeamsFilterSet(
        data={"q": "012345"}, queryset=Team.objects.all(),
    ).qs

    assert queryset.count() == 0


def test_order_by_title(user, make_team_leader):
    """
    Test order by title.

    :param user:
    :param make_team_leader:
    """
    teams = [
        TeamFactory.create(title="agent"),
        TeamFactory.create(title="cloud"),
        TeamFactory.create(title="bar"),
    ]

    make_team_leader(teams[0], user)
    make_team_leader(teams[1], user)
    make_team_leader(teams[2], user)

    queryset = TeamsFilterSet(
        data={"order_by": "title"}, queryset=Team.objects.all(),
    ).qs

    assert list(queryset) == lists.sub_list(teams, (0, 2, 1))

    queryset = TeamsFilterSet(
        data={"order_by": "-title"}, queryset=Team.objects.all(),
    ).qs

    assert list(queryset) == lists.sub_list(teams, (1, 2, 0))
