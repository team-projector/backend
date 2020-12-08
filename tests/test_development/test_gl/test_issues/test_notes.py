from collections import namedtuple

from apps.development.models.note import NoteType
from apps.development.services.issue.gl.manager import IssueGlManager
from tests.helpers.checkers import assert_instance_fields
from tests.test_development.factories.gitlab import GlNoteFactory
from tests.test_development.test_gl.helpers import (
    gl_checkers,
    gl_mock,
    initializers,
)
from tests.test_users.factories.gitlab import GlUserFactory

GL_LOADER = namedtuple(
    "GlLoader",
    ("issue", "gl_issue", "gl_note", "gl_author"),
)


def test_load_issue_notes(db, gl_mocker, gl_client):
    """
    Test load issue notes.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    gl_loader = _create_gl_loader(gl_mocker, gl_client)

    IssueGlManager().sync_notes(gl_loader.issue, gl_loader.gl_issue)

    note = gl_loader.issue.notes.first()

    assert note.created_at is not None
    assert note.updated_at is not None

    assert_instance_fields(
        note,
        gl_id=gl_loader.gl_note["id"],
        type=NoteType.TIME_SPEND,
        body="added 1h of time spent at 2000-01-01",
        content_object=gl_loader.issue,
        data={"date": "2000-01-01", "spent": 3600},
    )
    assert_instance_fields(note.user, login=gl_loader.gl_author["username"])
    gl_checkers.check_user(note.user, gl_loader.gl_author)


def _create_gl_loader(gl_mocker, gl_client) -> GL_LOADER:  # noqa: WPS210
    project, gl_project = initializers.init_project()
    issue, gl_issue = initializers.init_issue(project, gl_project)
    gl_author = GlUserFactory.create()
    gl_note = GlNoteFactory.create(
        author=gl_author,
        body="added 1h of time spent at 2000-01-01",
    )

    gl_mock.register_user(gl_mocker, gl_author)
    gl_mock.mock_project_endpoints(gl_mocker, gl_project)
    gl_mock.mock_issue_endpoints(
        gl_mocker,
        gl_project,
        gl_issue,
        notes=[gl_note],
    )

    return GL_LOADER(
        issue,
        gl_client.projects.get(id=project.gl_id).issues.get(id=issue.gl_iid),
        gl_note,
        gl_author,
    )
