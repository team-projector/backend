# -*- coding: utf-8 -*-

from django.test import override_settings

from apps.core.utils.objects import dict2obj
from apps.development.models import Project
from apps.development.services.project.gl.manager import ProjectGlManager
from tests.test_development.factories import ProjectGroupFactory
from tests.test_development.factories.gitlab import (
    GlHookFactory,
    GlProjectFactory,
)
from tests.test_development.test_gl.helpers import gl_checkers, gl_mock


def test_success(db, gl_mocker):
    group = ProjectGroupFactory.create()
    gl_project = GlProjectFactory.create()

    ProjectGlManager().update_project(group, dict2obj(gl_project))

    assert Project.objects.count() == 1
    project = Project.objects.first()

    gl_checkers.check_project(project, gl_project, group)


def test_bad_id(db, gl_mocker):
    group = ProjectGroupFactory.create()
    gl_project = GlProjectFactory.create(id="bad_gl_id")

    ProjectGlManager().update_project(group, dict2obj(gl_project))

    assert not Project.objects.exists()


@override_settings(GITLAB_CHECK_WEBHOOKS=True, DOMAIN_NAME="test.com")
def test_check_webhooks(db, gl_mocker, gl_client):
    group = ProjectGroupFactory.create()
    gl_project = GlProjectFactory.create()

    GlHookFactory.create(url="https://test1.com/api/1")
    webhook = GlHookFactory.create(
        url="https://test.com/api/gl_client-webhook",
    )

    gl_mock.mock_project_endpoints(gl_mocker, gl_project, hooks=[webhook])
    gl_mock.register_create_project_hook(
        gl_mocker, gl_project, {"id": gl_project["id"]},
    )

    gl_project_loaded = gl_client.projects.get(id=gl_project["id"])

    ProjectGlManager().update_project(group, gl_project_loaded)

    project = Project.objects.first()

    gl_checkers.check_project(project, gl_project, group)
