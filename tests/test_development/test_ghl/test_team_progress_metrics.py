from datetime import datetime

from pytest import raises

from apps.core.graphql.errors import GraphQLPermissionDenied
from apps.development.graphql.resolvers import resolve_team_progress_metrics
from apps.development.models import TeamMember
from tests.helpers.objects import AttrDict
from tests.test_development.factories import TeamFactory, TeamMemberFactory


def test_team_progress_metrics(user, client):
    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER
    )

    client.user = user
    info = AttrDict({'context': client})

    metrics = resolve_team_progress_metrics(
        parent=None,
        info=info,
        team=team.id,
        start=datetime.now().date(),
        end=datetime.now().date(),
        group='day'
    )

    assert len(metrics) == 1


def test_another_team(user, client):
    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER
    )

    another_team = TeamFactory.create()

    client.user = user
    info = AttrDict({'context': client})

    with raises(GraphQLPermissionDenied):
        resolve_team_progress_metrics(
            parent=None,
            info=info,
            team=another_team.id,
            start=datetime.now().date(),
            end=datetime.now().date(),
            group='day'
        )


def test_not_leader(user, client):
    team = TeamFactory.create()
    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.DEVELOPER
    )

    client.user = user
    info = AttrDict({'context': client})

    with raises(GraphQLPermissionDenied):
        resolve_team_progress_metrics(
            parent=None,
            info=info,
            team=team.id,
            start=datetime.now().date(),
            end=datetime.now().date(),
            group='day'
        )
