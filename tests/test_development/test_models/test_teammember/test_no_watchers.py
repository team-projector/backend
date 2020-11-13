import pytest

from apps.development.models import TeamMember
from tests.test_development.factories import TeamFactory, TeamMemberFactory


@pytest.mark.parametrize(
    ("roles", "count"),
    [
        (TeamMember.roles.LEADER, 1),
        (TeamMember.roles.DEVELOPER, 1),
        (TeamMember.roles.WATCHER, 0),
        (TeamMember.roles.LEADER | TeamMember.roles.DEVELOPER, 1),
        (TeamMember.roles.LEADER | TeamMember.roles.WATCHER, 1),
        (TeamMember.roles.DEVELOPER | TeamMember.roles.WATCHER, 1),
        (
            TeamMember.roles.LEADER
            | TeamMember.roles.DEVELOPER
            | TeamMember.roles.WATCHER,
            1,
        ),
    ],
)
def test_no_watchers(user, roles, count):
    """Test get no watchers."""
    team = TeamFactory.create()
    TeamMemberFactory.create(user=user, team=team, roles=roles)
    assert TeamMember.objects.get_no_watchers(team).count() == count


def test_no_watchers_another_team(user):
    """Test filter no watchers by team."""
    TeamMemberFactory.create(
        user=user,
        team=TeamFactory.create(),
        roles=TeamMember.roles.LEADER,
    )
    assert not TeamMember.objects.get_no_watchers(
        TeamFactory.create(),
    ).exists()
