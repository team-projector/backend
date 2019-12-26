from http import HTTPStatus

import pytest
from gitlab.exceptions import GitlabGetError

from apps.development.services.issue.gl.manager import IssueGlManager
from tests.test_development.factories import ProjectFactory
from tests.test_development.factories.gitlab import GlProjectFactory
from tests.test_development.test_gl.helpers import gl_mock


def test_server_error(db, gl_mocker):
    gl_project = GlProjectFactory.create()
    ProjectFactory.create(gl_id=gl_project['id'])
    gl_mock.register_project(
        gl_mocker,
        gl_project,
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    with pytest.raises(GitlabGetError):
        IssueGlManager().sync_issues()


def test_project_not_found(db, gl_mocker):
    gl_project = GlProjectFactory.create()
    ProjectFactory.create(gl_id=gl_project['id'])
    gl_mock.register_project(
        gl_mocker,
        gl_project,
        status_code=HTTPStatus.NOT_FOUND,
    )

    IssueGlManager().sync_issues()
