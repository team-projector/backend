from tests.test_development.test_gl.helpers.gl_mock import register_issue

KEY_ID = "id"
KEY_IID = "iid"


def mock_create_note_issue_endpoint(mocker, project, issue, response):
    """Mock create issue endpoint."""
    register_issue(mocker, project, issue)
    mocker.register_post(
        "/projects/{0}/issues/{1}/notes".format(
            project[KEY_ID],
            issue[KEY_IID],
        ),
        response,
    )
