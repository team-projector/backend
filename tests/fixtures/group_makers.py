import pytest

from apps.development.models.project_member import ProjectMember
from tests.test_development.factories import ProjectMemberFactory
from tests.test_users.factories import UserFactory


@pytest.fixture()
def make_group_manager():
    """Group manager maker."""
    return _make_group_manager


@pytest.fixture()
def make_group_developer():
    """Group developer maker."""
    return _make_group_developer


@pytest.fixture()
def make_group_customer():
    """Group customer maker."""
    return _make_group_customer


def _make_group_manager(group, user=None):
    """Create or bind group manager."""
    return _add_or_update_user_in_group(
        group,
        ProjectMember.roles.MANAGER,
        user,
    )


def _make_group_developer(group, user=None):
    """Create or bind group developer."""
    return _add_or_update_user_in_group(
        group,
        ProjectMember.roles.DEVELOPER,
        user,
    )


def _make_group_customer(group, user=None):
    """Create or bind group customer."""
    return _add_or_update_user_in_group(
        group,
        ProjectMember.roles.CUSTOMER,
        user,
    )


def _add_or_update_user_in_group(group, roles, user):
    """Create user and add into group with given role."""
    if not user:
        user = UserFactory.create()

    ProjectMemberFactory.create(user=user, roles=roles, owner=group)

    return user
