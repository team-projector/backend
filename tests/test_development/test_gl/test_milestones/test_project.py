# -*- coding: utf-8 -*-

from apps.development.models import Milestone
from apps.development.services.milestone.gl.manager import MilestoneGlManager
from tests.test_development.factories.gitlab import GlProjectMilestoneFactory
from tests.test_development.test_gl.helpers import (
    gl_checkers,
    gl_mock,
    initializers,
)


def test_all(db, gl_mocker):
    project, gl_project = initializers.init_project()
    gl_milestone = GlProjectMilestoneFactory.create()

    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        milestones=[gl_milestone],
    )

    MilestoneGlManager().sync_project_milestones(project)

    milestone = Milestone.objects.get(gl_id=gl_milestone["id"])
    gl_checkers.check_milestone(milestone, gl_milestone, project)


def test_single(db, gl_mocker):
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

    MilestoneGlManager().sync_project_milestone(project, gl_milestone["id"])

    milestone = Milestone.objects.get(gl_id=gl_milestone["id"])
    gl_checkers.check_milestone(milestone, gl_milestone, project)
