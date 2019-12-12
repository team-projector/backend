from apps.development.graphql.filters import TeamsFilterSet
from apps.development.models import Team, TeamMember
from tests.test_development.factories import TeamFactory, TeamMemberFactory


def test_filter_by_role(user, client):
    TeamFactory.create_batch(5)
    team = TeamFactory.create()

    TeamMemberFactory.create(user=user, team=team,
                             roles=TeamMember.roles.LEADER)

    client.user = user

    results = TeamsFilterSet(
        data={'roles': 'DEVELOPER'},
        queryset=Team.objects.all(),
        request=client,
    ).qs

    assert results.count() == 0

    results = TeamsFilterSet(
        data={'roles': 'LEADER'},
        queryset=Team.objects.all(),
        request=client,
    ).qs

    assert results.count() == 1
    assert results.first() == team


def test_filter_many_roles(user, client):
    TeamFactory.create_batch(5)
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER | TeamMember.roles.DEVELOPER
    )

    client.user = user

    results = TeamsFilterSet(
        data={'roles': 'LEADER'},
        queryset=Team.objects.all(),
        request=client,
    ).qs

    assert results.count() == 1
    assert results.first() == team

    results = TeamsFilterSet(
        data={'roles': 'DEVELOPER'},
        queryset=Team.objects.all(),
        request=client,
    ).qs

    assert results.first() == team

    results = TeamsFilterSet(
        data={'roles': 'WATCHER'},
        queryset=Team.objects.all(),
        request=client,
    ).qs

    assert results.count() == 0


def test_filter_by_user_and_many_roles(user, client):
    TeamFactory.create_batch(5)
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER | TeamMember.roles.DEVELOPER
    )

    client.user = user

    results = TeamsFilterSet(
        data={'roles': 'LEADER,WATCHER'},
        queryset=Team.objects.all(),
        request=client,
    ).qs

    assert results.count() == 1
    assert results.first() == team


def test_search(user):
    team_1 = TeamFactory.create(title='create')
    team_2 = TeamFactory.create(title='react')
    team_3 = TeamFactory.create(title='test0')

    TeamMemberFactory.create(user=user, team=team_1,
                             roles=TeamMember.roles.LEADER)
    TeamMemberFactory.create(user=user, team=team_2,
                             roles=TeamMember.roles.LEADER)
    TeamMemberFactory.create(user=user, team=team_3,
                             roles=TeamMember.roles.LEADER)

    results = TeamsFilterSet(
        data={'q': 'ate'},
        queryset=Team.objects.all()
    ).qs

    assert results.count() == 1
    assert results.first() == team_1

    results = TeamsFilterSet(
        data={'q': 'rea'},
        queryset=Team.objects.all(),
    ).qs

    assert results.count() == 2
    assert set(results) == {team_1, team_2}

    results = TeamsFilterSet(
        data={'q': '012345'},
        queryset=Team.objects.all()
    ).qs

    assert results.count() == 0


def test_order_by_title(user):
    team_1 = TeamFactory.create(title='agent')
    team_2 = TeamFactory.create(title='cloud')
    team_3 = TeamFactory.create(title='bar')

    TeamMemberFactory.create(user=user, team=team_1,
                             roles=TeamMember.roles.LEADER)
    TeamMemberFactory.create(user=user, team=team_2,
                             roles=TeamMember.roles.LEADER)
    TeamMemberFactory.create(user=user, team=team_3,
                             roles=TeamMember.roles.LEADER)

    results = TeamsFilterSet(
        data={'order_by': 'title'},
        queryset=Team.objects.all()
    ).qs

    assert list(results) == [team_1, team_3, team_2]

    results = TeamsFilterSet(
        data={'order_by': '-title'},
        queryset=Team.objects.all()
    ).qs

    assert list(results) == [team_2, team_3, team_1]
