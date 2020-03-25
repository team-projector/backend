# -*- coding: utf-8 -*-

from datetime import datetime

import pytest

from apps.core.graphql.errors import GraphQLNotFound
from apps.development.models import TeamMember
from apps.users.graphql.resolvers import resolve_user_progress_metrics
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_users.factories.user import UserFactory


def test_success(user, ghl_auth_mock_info):
    """Test sucess user metrics resolving."""
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user, team=team, roles=TeamMember.roles.LEADER,
    )

    checked_user = UserFactory.create()
    TeamMemberFactory.create(
        user=checked_user, team=team, roles=TeamMember.roles.DEVELOPER,
    )

    metrics = resolve_user_progress_metrics(
        parent=None,
        info=ghl_auth_mock_info,
        user=checked_user.pk,
        start=datetime.now().date(),
        end=datetime.now().date(),
        group="day",
    )

    assert len(metrics) == 1


def test_not_leader(user, ghl_auth_mock_info):
    """Test if user is not a leader."""
    team = TeamFactory.create()

    TeamMemberFactory.create(
        user=user, team=team, roles=TeamMember.roles.DEVELOPER,
    )

    checked_user = UserFactory.create()
    TeamMemberFactory.create(
        user=checked_user, team=team, roles=TeamMember.roles.DEVELOPER,
    )

    with pytest.raises(GraphQLNotFound):
        resolve_user_progress_metrics(
            parent=None,
            info=ghl_auth_mock_info,
            user=checked_user.pk,
            start=datetime.now().date(),
            end=datetime.now().date(),
            group="day",
        )
