import pytest

from tests.test_development.factories import TeamFactory


@pytest.fixture()
def team(db) -> None:
    """Create test team."""
    return TeamFactory.create()


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
    return make_team_leader(team)
