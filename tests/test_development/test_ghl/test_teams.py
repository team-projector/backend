from pytest import raises

from apps.core.graphql.errors import GraphQLNotFound
from apps.development.graphql.types import TeamType
from apps.development.models import Team, TeamMember
from tests.helpers.objects import AttrDict
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_users.factories.user import UserFactory


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

    with raises(GraphQLNotFound):
        TeamType().get_node(info, team.id)


def test_teams(user, client):
    team_1 = TeamFactory.create()
    TeamMemberFactory.create(user=user, team=team_1,
                             roles=TeamMember.roles.DEVELOPER)

    team_2 = TeamFactory.create()
    TeamMemberFactory.create(user=user, team=team_2,
                             roles=TeamMember.roles.DEVELOPER)
    TeamFactory.create_batch(5)

    client.user = user
    info = AttrDict({'context': client})

    teams = TeamType().get_queryset(Team.objects, info)

    assert set(teams) == {team_1, team_2}


def test_teams_not_member(user, client):
    team_1 = TeamFactory.create()
    TeamMemberFactory.create(user=user, team=team_1,
                             roles=TeamMember.roles.DEVELOPER)

    team_2 = TeamFactory.create()
    TeamMemberFactory.create(user=UserFactory.create(), team=team_2,
                             roles=TeamMember.roles.DEVELOPER)
    TeamFactory.create_batch(5)

    client.user = user
    info = AttrDict({'context': client})

    teams = TeamType().get_queryset(Team.objects, info)

    assert teams.count() == 1
    assert teams.first() == team_1


def test_resolver(user):
    team = TeamFactory.create()

    member_1 = TeamMemberFactory.create(
        user=user,
        team=team
    )
    member_2 = TeamMemberFactory.create(
        user=UserFactory.create(),
        team=team
    )

    members = TeamType.resolve_members(team, None).all()
    assert set(members) == {member_1, member_2}
