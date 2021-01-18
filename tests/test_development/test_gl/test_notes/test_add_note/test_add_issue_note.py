from collections import namedtuple

from apps.development.services.note.gitlab import add_issue_note
from tests.test_development.test_gl.helpers import gl_mock, initializers
from tests.test_users.factories.gitlab import GlUserFactory

ISSUE_DATA = namedtuple(
    "IssueData",
    ("project", "issue"),
)


def test_add_issue_note(user, gl_mocker, gl_client):
    """Test add issue note."""
    issue_data = _create_issue_data(gl_mocker)

    assert add_issue_note(user, issue_data.issue, "test") is None


def _create_issue_data(gl_mocker) -> ISSUE_DATA:
    """Generate issue data."""
    project, gl_project = initializers.init_project()
    issue, gl_issue = initializers.init_issue(project, gl_project)
    gl_user = GlUserFactory.create()

    gl_mock.register_user(gl_mocker, gl_user)
    gl_mock.mock_project_endpoints(
        gl_mocker,
        gl_project,
        issues=[gl_issue],
    )
    gl_mock.mock_issue_endpoints(
        gl_mocker,
        gl_project,
        gl_issue,
    )

    gl_mock.mock_create_note_issue_endpoint(
        gl_mocker,
        gl_project,
        gl_issue,
        {
            "id": 10,
            "body": "test note body",
        },
    )

    return ISSUE_DATA(project, issue)
