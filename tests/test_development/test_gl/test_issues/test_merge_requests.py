# -*- coding: utf-8 -*-

from apps.development.models import Issue
from apps.development.services.issue.gl.manager import IssueGlManager
from tests.test_development.factories.gitlab import GlMergeRequestFactory
from tests.test_development.test_gl.helpers import gl_mock, initializers
from tests.test_users.factories.gitlab import GlUserFactory


def test_load_merge_requests(db, gl_mocker, gl_client):
    project, gl_project = initializers.init_project()
    issue, gl_issue = initializers.init_issue(project, gl_project)
    gl_user = GlUserFactory.create()
    gl_merge_request = GlMergeRequestFactory.create(
        project_id=gl_project["id"],
        assignee=gl_user,
        author=gl_user,
    )

    gl_mock.register_user(gl_mocker, gl_user)
    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        issues=[gl_issue],
        merge_requests=[gl_merge_request],
    )
    gl_mock.mock_issue_endpoints(
        gl_mocker,
        gl_project,
        gl_issue,
        closed_by=[gl_merge_request]
    )
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_project,
        gl_merge_request,
    )

    gl_project = gl_client.projects.get(id=project.gl_id)
    gl_issue = gl_project.issues.get(id=issue.gl_iid)

    assert not issue.merge_requests.exists()

    IssueGlManager().sync_merge_requests(issue, project, gl_issue, gl_project)

    issue = Issue.objects.first()

    assert issue.merge_requests.count() == 1
    assert issue.merge_requests.first().gl_id == gl_merge_request["id"]
