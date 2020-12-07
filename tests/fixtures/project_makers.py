import pytest

from apps.development.models.project_member import ProjectMember
from tests.test_development.factories import ProjectMemberFactory
from tests.test_users.factories import UserFactory


@pytest.fixture()
def make_project_manager():
    """Project manager maker."""
    return _make_project_manager


@pytest.fixture()
def make_project_developer():
    """Project developer maker."""
    return _make_project_developer


@pytest.fixture()
def make_project_customer():
    """Project customer maker."""
    return _make_project_customer


def _make_project_manager(project, user=None):
    """Create or bind project manager."""
    return _add_or_update_user_in_project(
        project,
        ProjectMember.roles.MANAGER,
        user,
    )


def _make_project_developer(project, user=None):
    """Create or bind project developer."""
    return _add_or_update_user_in_project(
        project,
        ProjectMember.roles.DEVELOPER,
        user,
    )


def _make_project_customer(project, user=None):
    """Create or bind project customer."""
    return _add_or_update_user_in_project(
        project,
        ProjectMember.roles.CUSTOMER,
        user,
    )


def _add_or_update_user_in_project(project, roles, user):
    """Create user and add into project with given role."""
    if not user:
        user = UserFactory.create()

    ProjectMemberFactory.create(user=user, roles=roles, owner=project)

    return user
