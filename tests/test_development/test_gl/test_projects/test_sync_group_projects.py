# -*- coding: utf-8 -*-

from apps.development.models import Project
from apps.development.services.project.gl.manager import ProjectGlManager
from tests.test_development.factories.gitlab import GlProjectFactory
from tests.test_development.test_gl.helpers import (
    gl_checkers,
    gl_mock,
    initializers,
)


def test_from_one_group(db, gl_mocker, gl_client):
    """
    Test from one group.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    group, gl_group = initializers.init_group()
    gl_project = GlProjectFactory.create()

    gl_mock.mock_group_endpoints(gl_mocker, gl_group, projects=[gl_project])

    ProjectGlManager().sync_group_projects(group)

    project = Project.objects.get(gl_id=gl_project["id"])
    gl_checkers.check_project(project, gl_project, group)


def test_shared_with_group(db, gl_mocker, gl_client):
    """
    Test from one group.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    group, gl_group = initializers.init_group()
    gl_project = GlProjectFactory.create()
    gl_project["shared_with_groups"] = [{"group_id": gl_group["id"]}]

    gl_mock.mock_group_endpoints(gl_mocker, gl_group, projects=[gl_project])

    ProjectGlManager().sync_group_projects(group)

    assert not Project.objects.exists()
