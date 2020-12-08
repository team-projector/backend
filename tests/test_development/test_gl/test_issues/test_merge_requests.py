from collections import namedtuple

from apps.development.models import Issue
from apps.development.services.issue.gl.manager import IssueGlManager
from tests.test_development.factories.gitlab import GlMergeRequestFactory
from tests.test_development.test_gl.helpers import gl_mock, initializers
from tests.test_users.factories.gitlab import GlUserFactory

MERGE_REQUEST_DATA = namedtuple(
    "MergeRequestData",
    ("project", "issue", "gl_merge_request"),
)


def test_load_merge_requests(db, gl_mocker, gl_client):
    """
    Test load merge requests.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    merge_request_data = _create_merge_request_data(gl_mocker)

    gl_project = gl_client.projects.get(id=merge_request_data.project.gl_id)
    gl_issue = gl_project.issues.get(id=merge_request_data.issue.gl_iid)

    assert not merge_request_data.issue.merge_requests.exists()

    IssueGlManager().sync_merge_requests(
        merge_request_data.issue,
        merge_request_data.project,
        gl_issue,
        gl_project,
    )

    issue = Issue.objects.first()

    assert issue.merge_requests.count() == 1
    assert (
        issue.merge_requests.first().gl_id
        == merge_request_data.gl_merge_request["id"]
    )


def _create_merge_request_data(  # noqa: WPS210
    gl_mocker,
) -> MERGE_REQUEST_DATA:
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
        closed_by=[gl_merge_request],
    )
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_project,
        gl_merge_request,
    )

    return MERGE_REQUEST_DATA(project, issue, gl_merge_request)
