from apps.development.models import Milestone
from apps.development.services.milestone.gl.manager import MilestoneGlManager
from tests.test_development.factories import ProjectGroupMilestoneFactory
from tests.test_development.factories.gitlab import GlProjectMilestoneFactory
from tests.test_development.test_gl.helpers import (
    gl_checkers,
    gl_mock,
    initializers,
)

KEY_ID = "id"


def test_all(db, gl_mocker):
    """
    Test all.

    :param db:
    :param gl_mocker:
    """
    project, gl_project = initializers.init_project()
    gl_milestone = GlProjectMilestoneFactory.create(group_id=None)

    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        milestones=[gl_milestone],
    )

    MilestoneGlManager().sync_project_milestones(project)

    milestone = Milestone.objects.get(gl_id=gl_milestone[KEY_ID])
    gl_checkers.check_milestone(milestone, gl_milestone, project)
    assert (
        list(
            project.milestones.filter(projectmilestone__is_inherited=False),
        )
        == [milestone]
    )


def test_inheriting_milestones(db, gl_mocker):
    """
    Test inheriting milestones.

    :param db:
    :param gl_mocker:
    """
    project, gl_project = initializers.init_project()
    gl_milestone1 = GlProjectMilestoneFactory.create()
    gl_milestone2 = GlProjectMilestoneFactory.create(project_id=None)
    group_milestone = ProjectGroupMilestoneFactory.create(
        gl_id=gl_milestone2[KEY_ID],
    )

    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        milestones=[gl_milestone1, gl_milestone2],
    )

    MilestoneGlManager().sync_project_milestones(project)

    assert (
        list(
            project.milestones.filter(projectmilestone__is_inherited=True),
        )
        == [group_milestone]
    )


def test_owner(db, gl_mocker):
    """
    Test inheriting milestones.

    :param db:
    :param gl_mocker:
    """
    project, gl_project = initializers.init_project()
    gl_milestone1 = GlProjectMilestoneFactory.create(
        project_id=gl_project["id"],
        group_id=None,
    )
    gl_milestone2 = GlProjectMilestoneFactory.create(project_id=None)
    group_milestone = ProjectGroupMilestoneFactory.create(
        gl_id=gl_milestone2[KEY_ID],
    )

    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        milestones=[gl_milestone1, gl_milestone2],
    )

    MilestoneGlManager().sync_project_milestones(project)

    assert (
        list(
            project.milestones.filter(projectmilestone__is_inherited=True),
        )
        == [group_milestone]
    )
    assert (
        project.milestones.filter(
            projectmilestone__is_inherited=False,
        ).count()
        == 1
    )


def test_single(db, gl_mocker):
    """
    Test single.

    :param db:
    :param gl_mocker:
    """
    project, gl_project = initializers.init_project()
    gl_milestone = GlProjectMilestoneFactory.create()

    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        milestones=[gl_milestone],
    )

    gl_mock.mock_project_milestone_endpoints(
        gl_mocker,
        gl_project,
        gl_milestone,
    )

    MilestoneGlManager().sync_project_milestone(project, gl_milestone[KEY_ID])

    milestone = Milestone.objects.get(gl_id=gl_milestone[KEY_ID])
    gl_checkers.check_milestone(milestone, gl_milestone, project)
