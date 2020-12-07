import pytest

from apps.development.models.project_member import ProjectMember
from apps.development.services.project.members import get_project_managers
from tests.test_development.factories import (
    ProjectGroupFactory,
    ProjectMemberFactory,
)


@pytest.fixture()
def project_group(project):
    """Create project group."""
    group = ProjectGroupFactory.create()
    project.group = group
    project.save()

    return group


def test_project_manager(project):
    """Test manager in project."""
    manager = ProjectMemberFactory.create(
        owner=project,
        roles=ProjectMember.roles.MANAGER,
    )

    assert set(get_project_managers(project)) == {manager.user}
    assert not get_project_managers(None)


def test_many_managers(project):
    """Test many managers in project."""
    managers = ProjectMemberFactory.create_batch(
        2,
        owner=project,
        roles=ProjectMember.roles.MANAGER,
    )

    assert set(get_project_managers(project)) == {
        manager.user for manager in managers
    }


def test_project_not_manager(project):
    """Test not manager."""
    ProjectMemberFactory.create(
        owner=project,
        roles=ProjectMember.roles.DEVELOPER,
    )

    assert not get_project_managers(project)


def test_project_manager_and_developer(project):
    """Test manager and not manager in project."""
    ProjectMemberFactory.create(
        owner=project,
        roles=ProjectMember.roles.DEVELOPER,
    )
    manager = ProjectMemberFactory.create(
        owner=project,
        roles=ProjectMember.roles.MANAGER,
    )

    assert set(get_project_managers(project)) == {manager.user}


def test_groups(project, project_group):
    """Test manager in project group."""
    manager = ProjectMemberFactory.create(
        owner=project_group,
        roles=ProjectMember.roles.MANAGER,
    )

    assert set(get_project_managers(project)) == {manager.user}


def test_groups_inheritance(project, project_group):
    """Test manager in groups inheritance."""
    parent_group = ProjectGroupFactory.create()
    project_group.parent = parent_group
    project_group.save()

    manager_parent = ProjectMemberFactory.create(
        owner=parent_group,
        roles=ProjectMember.roles.MANAGER,
    )
    manager_group = ProjectMemberFactory.create(
        owner=project_group,
        roles=ProjectMember.roles.MANAGER,
    )

    assert set(get_project_managers(project)) == {
        manager_parent.user,
        manager_group.user,
    }
