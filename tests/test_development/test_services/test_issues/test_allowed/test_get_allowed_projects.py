import pytest

from apps.development.models import ProjectMember
from apps.development.services.issue.allowed import get_allowed_projects
from tests.test_development.factories import (
    ProjectFactory,
    ProjectGroupFactory,
    ProjectMemberFactory,
)


@pytest.fixture()
def project_group(project):
    """Create project group."""
    project.group = ProjectGroupFactory.create()
    project.save()

    return project.group


def test_direct_project(user, project):
    """Test user is member for current project."""
    ProjectMemberFactory.create(
        user=user,
        owner=project,
        roles=ProjectMember.roles.MANAGER,
    )
    ProjectMemberFactory.create(
        user=user,
        owner=ProjectFactory.create(),
        roles=ProjectMember.roles.DEVELOPER,
    )

    assert get_allowed_projects(user) == {project}


def test_not_manager(user, project):
    """Test user is member for current project not manager."""
    ProjectMemberFactory.create(
        user=user,
        owner=project,
        roles=ProjectMember.roles.DEVELOPER,
    )

    assert not get_allowed_projects(user)


def test_manager_and_developer(user, project):
    """Test user is member for current project not manager."""
    ProjectMemberFactory.create(
        user=user,
        owner=project,
        roles=ProjectMember.roles.DEVELOPER | ProjectMember.roles.MANAGER,
    )

    assert get_allowed_projects(user) == {project}


def test_group_member_manager(user, project_group, project):
    """Test get projects as group member-manager."""
    ProjectMemberFactory.create(
        user=user,
        owner=project_group,
        roles=ProjectMember.roles.MANAGER,
    )

    assert get_allowed_projects(user) == {project}


def test_group_member_developer(user, project_group, project):
    """Test get projects as group member-developer."""
    ProjectMemberFactory.create(
        user=user,
        owner=project_group,
        roles=ProjectMember.roles.DEVELOPER,
    )

    assert not get_allowed_projects(user)


def test_group_and_project_member_manager(user, project_group, project):
    """Test get projects as group member-developer."""
    ProjectMemberFactory.create(
        user=user,
        owner=project_group,
        roles=ProjectMember.roles.MANAGER,
    )

    ProjectMemberFactory.create(
        user=user,
        owner=ProjectGroupFactory.create(),
        roles=ProjectMember.roles.MANAGER,
    )

    another_project = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=user,
        owner=another_project,
        roles=ProjectMember.roles.MANAGER,
    )

    assert get_allowed_projects(user) == {project, another_project}
