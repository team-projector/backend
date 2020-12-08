from collections import namedtuple

from apps.development.services.issue.gl.manager import IssueGlManager
from tests.test_development.test_gl.helpers import (
    gl_checkers,
    gl_mock,
    initializers,
)
from tests.test_users.factories.gitlab import GlUserFactory

GL_LOADER = namedtuple(
    "GlLoader",
    ("project", "issue", "gl_project", "gl_issue", "gl_participants"),
)


def test_participants(db, gl_mocker, gl_client):
    """
    Test participants.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    gl_loader = _create_gitlab_loader(gl_mocker, gl_client)

    IssueGlManager().sync_participants(gl_loader.issue, gl_loader.gl_issue)

    for gl_participant in gl_loader.gl_participants:
        participant = gl_loader.issue.participants.get(
            login=gl_participant["username"],
        )
        gl_checkers.check_user(participant, gl_participant)


def _create_gitlab_loader(gl_mocker, gl_client) -> GL_LOADER:  # noqa: WPS210
    project, gl_project = initializers.init_project()
    issue, gl_issue = initializers.init_issue(project, gl_project)
    gl_participants = GlUserFactory.create_batch(2)

    for to_register in gl_participants:
        gl_mock.register_user(gl_mocker, to_register)

    gl_mock.mock_project_endpoints(gl_mocker, gl_project)
    gl_mock.mock_issue_endpoints(
        gl_mocker,
        gl_project,
        gl_issue,
        participants=gl_participants,
    )

    return GL_LOADER(
        project,
        issue,
        gl_client.projects.get(id=project.gl_id),
        gl_client.projects.get(id=project.gl_id).issues.get(id=issue.gl_iid),
        gl_participants,
    )
