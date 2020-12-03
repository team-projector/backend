from apps.development.models import Milestone
from apps.development.services.milestone.gl.manager import MilestoneGlManager
from tests.test_development.factories.gitlab import GlGroupMilestoneFactory
from tests.test_development.test_gl.helpers import (
    gl_checkers,
    gl_mock,
    initializers,
)


def test_all(db, gl_mocker):
    """
    Test all.

    :param db:
    :param gl_mocker:
    """
    group, gl_group = initializers.init_group()
    gl_milestone = GlGroupMilestoneFactory.create(group_id=gl_group["id"])

    gl_mock.mock_group_endpoints(
        gl_mocker,
        gl_group,
        milestones=[gl_milestone],
    )

    MilestoneGlManager().sync_project_group_milestones(group)

    milestone = Milestone.objects.get(gl_id=gl_milestone["id"])
    gl_checkers.check_milestone(milestone, gl_milestone, group)
    assert (
        list(
            group.milestones.filter(projectgroupmilestone__is_inherited=False),
        )
        == [milestone]
    )


def test_single(db, gl_mocker):
    """
    Test single.

    :param db:
    :param gl_mocker:
    """
    group, gl_group = initializers.init_group()
    gl_milestone = GlGroupMilestoneFactory.create()

    gl_mock.mock_group_endpoints(
        gl_mocker,
        gl_group,
        milestones=[gl_milestone],
    )
    gl_mock.mock_group_milestone_endpoints(gl_mocker, gl_group, gl_milestone)

    MilestoneGlManager().sync_project_group_milestone(
        group,
        gl_milestone["id"],
    )

    milestone = Milestone.objects.get(gl_id=gl_milestone["id"])
    gl_checkers.check_milestone(milestone, gl_milestone, group)
