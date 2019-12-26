# -*- coding: utf-8 -*-

from http import HTTPStatus

import pytest
from gitlab.exceptions import GitlabGetError

from apps.development.models import Issue
from apps.development.services.issue.gl.manager import IssueGlManager
from tests.test_development.factories import IssueFactory, ProjectFactory
from tests.test_development.factories.gitlab import GlProjectFactory
from tests.test_development.test_gl.helpers import gl_mock, initializers
from tests.test_users.factories.gitlab import GlUserFactory


def test_check_deleted(db, gl_mocker, gl_client):
    project, gl_project = initializers.init_project()
    gl_assignee = GlUserFactory.create()
    issue, gl_issue = initializers.init_issue(
        project,
        gl_project,
        gl_kwargs={
            'assignee': gl_assignee,
        },
    )
    IssueFactory.create_batch(5, project=project)

    gl_mock.register_user(gl_mocker, gl_assignee)
    gl_mock.mock_project_endpoints(gl_mocker, gl_project, issues=[gl_issue])

    IssueGlManager().check_project_deleted_issues(
        project,
        gl_client.projects.get(id=project.gl_id),
    )

    assert Issue.objects.count() == 1
    assert Issue.objects.filter(id=issue.id).exists()


def test_server_error(db, gl_mocker, gl_client):
    gl_project = GlProjectFactory.create()
    project = ProjectFactory.create(gl_id=gl_project['id'])

    gl_mock.register_project(
        gl_mocker,
        gl_project,
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    with pytest.raises(GitlabGetError):
        IssueGlManager().check_project_deleted_issues(
            project,
            gl_client.projects.get(id=project.gl_id),
        )
