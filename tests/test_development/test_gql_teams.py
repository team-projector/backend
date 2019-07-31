from apps.development.graphql.types import TeamType
from apps.development.graphql.filters import TeamsFilterSet
from apps.development.models import TeamMember, Team
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_users.factories import UserFactory
from tests.test_development.factories_gitlab import AttrDict


def test_list(user, client):
    team_1 = TeamFactory.create()
    TeamMemberFactory.create(user=user, team=team_1,
                             roles=TeamMember.roles.developer)

    team_2 = TeamFactory.create()
    TeamMemberFactory.create(user=user, team=team_2,
                             roles=TeamMember.roles.developer)
    TeamFactory.create_batch(5)

    client.user = user
    info = AttrDict({'context': client})

    teams = TeamType().get_queryset(Team.objects, info)

    assert set(teams) == {team_1, team_2}


def test_filter_member(user, client):
    TeamFactory.create_batch(5)
    team = TeamFactory.create()

    TeamMemberFactory.create(user=user, team=team,
                             roles=TeamMember.roles.leader)

    client.user = user
    info = AttrDict({'context': client})

    teams = TeamType().get_queryset(Team.objects, info)

    results = TeamsFilterSet(
        data={'roles': 'leader'},
        queryset=teams,
        request=client,
    ).qs

    assert results.count() == 1
    assert results.first() == team


def test_filter_not_member(user, client):
    TeamFactory.create_batch(5)

    client.user = user
    info = AttrDict({'context': client})

    teams = TeamType().get_queryset(Team.objects, info)

    results = TeamsFilterSet(
        data={'roles': 'leader'},
        queryset=teams,
        request=client,
    ).qs

    assert results.count() == 0


def test_filter_another_member(user, client):
    TeamFactory.create_batch(5)
    team = TeamFactory.create()

    user_2 = UserFactory.create()

    TeamMemberFactory.create(user=user_2, team=team,
                             roles=TeamMember.roles.leader)

    client.user = user
    info = AttrDict({'context': client})

    teams = TeamType().get_queryset(Team.objects, info)

    results = TeamsFilterSet(
        data={'roles': 'leader'},
        queryset=teams,
        request=client,
    ).qs

    assert results.count() == 0


def test_filter_member_bad_role(user, client):
    TeamFactory.create_batch(5)
    team = TeamFactory.create()

    TeamMemberFactory.create(user=user, team=team,
                             roles=TeamMember.roles.leader)

    client.user = user
    info = AttrDict({'context': client})

    teams = TeamType().get_queryset(Team.objects, info)

    results = TeamsFilterSet(
        data={'roles': 'developer'},
        queryset=teams,
        request=client,
    ).qs

    assert results.count() == 0


def test_filter_many_roles(user, client):
    TeamFactory.create_batch(5)
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader | TeamMember.roles.developer
    )

    client.user = user
    info = AttrDict({'context': client})

    teams = TeamType().get_queryset(Team.objects, info)

    results = TeamsFilterSet(
        data={'roles': 'leader'},
        queryset=teams,
        request=client,
    ).qs

    assert results.count() == 1
    assert results.first() == team


def test_filter_by_user_and_many_roles(user, client):
    TeamFactory.create_batch(5)
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.leader | TeamMember.roles.developer
    )

    client.user = user
    info = AttrDict({'context': client})

    teams = TeamType().get_queryset(Team.objects, info)

    results = TeamsFilterSet(
        data={'roles': 'leader,watcher'},
        queryset=teams,
        request=client,
    ).qs

    assert results.count() == 1
    assert results.first() == team


def test_team(user, client):
    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team
    )

    client.user = user
    info = AttrDict({'context': client})

    assert TeamType().get_node(info, team.id) == team


def test_team_not_member(user, client):
    team = TeamFactory.create()

    client.user = user
    info = AttrDict({'context': client})

    assert TeamType().get_node(info, team.id) is None
