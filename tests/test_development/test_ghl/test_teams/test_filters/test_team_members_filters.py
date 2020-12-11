from apps.development.graphql.filters import TeamMembersFilterSet
from apps.development.models import TeamMember
from tests.test_development.factories import TeamFactory, TeamMemberFactory
from tests.test_users.factories.user import UserFactory

KEY_ROLES = "roles"


def test_filter_by_role_developer(user):
    """
    Test filter by role developer.

    :param user:
    """
    _prepare_data()

    queryset = TeamMembersFilterSet(
        data={KEY_ROLES: "DEVELOPER"},
        queryset=TeamMember.objects.all(),
    ).qs

    assert queryset.count() == 2


def test_filter_by_role_leader(user):
    """
    Test filter by role leader.

    :param user:
    """
    _prepare_data()

    queryset = TeamMembersFilterSet(
        data={KEY_ROLES: "LEADER"},
        queryset=TeamMember.objects.all(),
    ).qs

    assert queryset.count() == 1


def test_filter_by_role_watcher(user):
    """
    Test filter by role watcher.

    :param user:
    """
    _prepare_data()

    queryset = TeamMembersFilterSet(
        data={KEY_ROLES: "WATCHER"},
        queryset=TeamMember.objects.all(),
    ).qs

    assert queryset.count() == 1


def test_filter_by_incorrect_role(user):
    """
    Test filter by incorrect role.

    :param user:
    """
    _prepare_data()

    queryset = TeamMembersFilterSet(
        data={KEY_ROLES: "incorrect value"},
        queryset=TeamMember.objects.all(),
    ).qs

    assert queryset.count() == 4


def test_filter_by_none_role(user):
    """
    Test filter by none role.

    :param user:
    """
    _prepare_data()

    queryset = TeamMembersFilterSet(
        data={KEY_ROLES: None},
        queryset=TeamMember.objects.all(),
    ).qs

    assert queryset.count() == 4


def _prepare_data():
    """Prepare data."""
    users = UserFactory.create_batch(2)
    teams = TeamFactory.create_batch(2)

    TeamMemberFactory.create(
        user=users[0],
        team=teams[0],
        roles=TeamMember.roles.LEADER,
    )
    TeamMemberFactory.create(
        user=users[1],
        team=teams[0],
        roles=TeamMember.roles.DEVELOPER,
    )

    TeamMemberFactory.create(
        user=users[0],
        team=teams[1],
        roles=TeamMember.roles.WATCHER,
    )
    TeamMemberFactory.create(
        user=users[1],
        team=teams[1],
        roles=TeamMember.roles.DEVELOPER,
    )
