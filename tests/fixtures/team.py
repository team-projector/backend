# -*- coding: utf-8 -*-

import pytest

from apps.development.models import TeamMember
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_users.factories import UserFactory


@pytest.fixture()
def team(db) -> None:
    """Create test team."""
    return TeamFactory.create()


@pytest.fixture()
def make_team_developer():
    """Team developer user maker."""
    return _make_team_developer


@pytest.fixture()
def make_team_leader():
    """Team leader user maker."""
    return _make_team_leader


@pytest.fixture()
def make_team_watcher():
    """Team watcher user maker."""
    return _make_team_watcher


@pytest.fixture()
def team_developer(team, make_team_developer) -> None:
    """Create team developer user."""
    return make_team_developer(team)


@pytest.fixture()
def team_watcher(team, make_team_watcher):
    """Create team watcher user."""
    return make_team_watcher(team)


@pytest.fixture()
def team_leader(team, make_team_leader):
    """Create team leader user."""
    return _make_team_leader(team)


def _make_team_developer(team, user=None):
    return _add_or_update_user_in_team(team, TeamMember.roles.DEVELOPER, user)


def _make_team_watcher(team, user=None):
    return _add_or_update_user_in_team(team, TeamMember.roles.WATCHER, user)


def _make_team_leader(team, user=None):
    return _add_or_update_user_in_team(team, TeamMember.roles.LEADER, user)


def _add_or_update_user_in_team(team, role, user):
    if not user:
        user = UserFactory.create()

    TeamMemberFactory.create(user=user, team=team, roles=role)

    return user
