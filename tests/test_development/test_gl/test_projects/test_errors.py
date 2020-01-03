# -*- coding: utf-8 -*-

from http import HTTPStatus

import pytest
from gitlab.exceptions import GitlabGetError

from apps.development.services.project.gl.manager import ProjectGlManager
from apps.development.services.project.gl.provider import ProjectGlProvider
from tests.test_development.test_gl.helpers import gl_mock, initializers


def test_server_error(db, gl_mocker):
    group, gl_group = initializers.init_group()
    gl_mock.register_group(
        gl_mocker,
        gl_group,
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    with pytest.raises(GitlabGetError):
        ProjectGlManager().sync_group_projects(group)


def test_not_found(db, gl_mocker):
    group, gl_group = initializers.init_group()
    gl_mock.register_group(
        gl_mocker,
        gl_group,
        status_code=HTTPStatus.NOT_FOUND,
    )

    ProjectGlManager().sync_group_projects(group)


def test_deactivate_if_not_found(db, gl_mocker):
    project, gl_project = initializers.init_project(model_kwargs={
        "is_active": False
    })

    gl_mock.register_project(
        gl_mocker,
        gl_project,
        status_code=HTTPStatus.NOT_FOUND,
    )

    ProjectGlProvider().get_gl_project(project)

    project.refresh_from_db()

    assert not project.is_active
