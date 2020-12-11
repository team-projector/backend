from apps.development.graphql.filters import MilestonesFilterSet
from apps.development.models import Milestone
from apps.development.services.milestone.gl.manager import MilestoneGlManager
from tests.test_development.factories import ProjectGroupMilestoneFactory
from tests.test_development.factories.gitlab import GlProjectMilestoneFactory
from tests.test_development.test_gl.helpers import gl_mock, initializers

KEY_PROJECT = "project"


def test_empty_filter(milestones):
    """Test not filter."""
    filter_set = MilestonesFilterSet(
        {KEY_PROJECT: None},
        queryset=Milestone.objects,
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 4


def test_filter_by_project_empty(project, milestones):
    """Test filter by project."""
    filter_set = MilestonesFilterSet(
        {KEY_PROJECT: project.pk},
        queryset=Milestone.objects,
    )

    assert filter_set.is_valid()
    assert not filter_set.qs.exists()


def test_filter_by_project(project, milestones):
    """Test filter by project."""
    project.milestones.add(milestones[2])

    _assert_filter_set({KEY_PROJECT: project.pk}, milestones[2])


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

    _assert_filter_set({KEY_PROJECT: project.pk}, group_milestone)


def _assert_filter_set(query, value_result) -> None:
    filter_set = MilestonesFilterSet(
        query,
        queryset=Milestone.objects,
    )

    assert filter_set.is_valid()
    assert filter_set.qs.count() == 1
    assert filter_set.qs.first() == value_result
