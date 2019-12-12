from datetime import datetime

from django.http.response import Http404
from pytest import raises
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_development.factories_gitlab import AttrDict
from tests.test_users.factories.user import UserFactory

from apps.development.models import TeamMember
from apps.users.graphql.resolvers import resolve_user_progress_metrics


def test_user_progress_metrics(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.LEADER
    )

    user_2 = UserFactory.create()
    TeamMemberFactory.create(
        user=user_2,
        team=team,
        roles=TeamMember.roles.DEVELOPER
    )

    client.user = user
    info = AttrDict({'context': client})

    metrics = resolve_user_progress_metrics(
        parent=None,
        info=info,
        user=user_2.id,
        start=datetime.now().date(),
        end=datetime.now().date(),
        group='day'
    )

    assert len(metrics) == 1


def test_user_progress_metrics_not_leader(user, client):
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user,
        team=team,
        roles=TeamMember.roles.DEVELOPER
    )

    user_2 = UserFactory.create()
    TeamMemberFactory.create(
        user=user_2,
        team=team,
        roles=TeamMember.roles.DEVELOPER
    )

    client.user = user
    info = AttrDict({'context': client})

    with raises(Http404):
        resolve_user_progress_metrics(
            parent=None,
            info=info,
            user=user_2.id,
            start=datetime.now().date(),
            end=datetime.now().date(),
            group='day'
        )
