from datetime import datetime

from django.core.exceptions import PermissionDenied
from pytest import raises

from apps.development.graphql.resolvers import resolve_team_progress_metrics
from apps.development.models import TeamMember
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_development.factories_gitlab import AttrDict


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

    with raises(PermissionDenied):
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

    with raises(PermissionDenied):
        resolve_team_progress_metrics(
            parent=None,
            info=info,
            team=team.id,
            start=datetime.now().date(),
            end=datetime.now().date(),
            group='day'
        )
