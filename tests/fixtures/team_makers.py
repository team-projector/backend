from typing import Optional

import pytest

from apps.development.models import Team, TeamMember
from apps.users.models import User
from tests.test_development.factories import TeamMemberFactory
from tests.test_users.factories import UserFactory


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


def _make_team_developer(team, user=None):
    return _add_or_update_user_in_team(team, TeamMember.roles.DEVELOPER, user)


def _make_team_watcher(team, user=None):
    return _add_or_update_user_in_team(team, TeamMember.roles.WATCHER, user)


def _make_team_leader(team, user=None):
    return _add_or_update_user_in_team(team, TeamMember.roles.LEADER, user)


def _add_or_update_user_in_team(team: Team, role: int, user: Optional[User]):
    if not user:
        user = UserFactory.create()

    TeamMemberFactory.create(user=user, team=team, roles=role)

    return user
