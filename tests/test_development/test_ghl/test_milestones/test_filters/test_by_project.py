import pytest

from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.models import Milestone
from apps.development.services.milestone.gl.manager import MilestoneGlManager
from tests.test_development.factories import (
    ProjectFactory,
    ProjectGroupFactory,
    ProjectGroupMilestoneFactory,
    ProjectMilestoneFactory,
)
from tests.test_development.factories.gitlab import GlProjectMilestoneFactory
from tests.test_development.test_gl.helpers import gl_mock, initializers


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


def test_empty_filter(milestones):
    """Test not filter."""
    filter_set = MilestonesFilterSet(
        {"project": None},
        queryset=Milestone.objects,
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 4


def test_filter_by_project_empty(project, milestones):
    """Test filter by project."""
    filter_set = MilestonesFilterSet(
        {"project": project.pk},
        queryset=Milestone.objects,
    )

    assert filter_set.is_valid()
    assert not filter_set.qs.exists()


def test_filter_by_project(project, milestones):
    """Test filter by project."""
    project.milestones.add(milestones[2])

    filter_set = MilestonesFilterSet(
        {"project": project.pk},
        queryset=Milestone.objects,
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 1
    assert filter_set.qs.first() == milestones[2]


def test_filter_inherit(db, gl_mocker):
    """Test get milestone for project group."""
    project, gl_project = initializers.init_project()
    gl_milestone1 = GlProjectMilestoneFactory.create()
    gl_milestone2 = GlProjectMilestoneFactory.create(project_id=None)
    group_milestone = ProjectGroupMilestoneFactory.create(
        gl_id=gl_milestone1["id"],
    )

    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        milestones=[gl_milestone1, gl_milestone2],
    )

    MilestoneGlManager().sync_project_milestones(project)

    filter_set = MilestonesFilterSet(
        {"project": project.pk},
        queryset=Milestone.objects,
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 1
    assert filter_set.qs.first() == group_milestone
