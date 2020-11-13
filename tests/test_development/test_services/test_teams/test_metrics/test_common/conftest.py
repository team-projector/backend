import pytest

from apps.development.models import TeamMember
from tests.test_development.factories import TeamFactory
from tests.test_users.factories import UserFactory


@pytest.fixture()
def team(user):
    """
    Team.

    :param user:
    """
    team = TeamFactory.create(members=UserFactory.create_batch(2))
    TeamMember.objects.filter(user__in=team.members.all()).update(
        roles=TeamMember.roles.LEADER,
    )

    return team
