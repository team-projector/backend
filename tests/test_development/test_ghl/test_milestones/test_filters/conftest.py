import pytest

from tests.test_development.factories import (
    ProjectFactory,
    ProjectGroupFactory,
    ProjectMilestoneFactory,
)


@pytest.fixture()
def project_group(db):
    """Create project group."""
    return ProjectGroupFactory.create()


@pytest.fixture()
def project(project_group):
    """Create project."""
    return ProjectFactory.create(group=project_group)


@pytest.fixture()
def milestones(db):
    """Create project milestones."""
    return ProjectMilestoneFactory.create_batch(4)
