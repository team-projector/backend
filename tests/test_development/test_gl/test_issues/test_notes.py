# -*- coding: utf-8 -*-

from apps.development.models.note import NoteType
from apps.development.services.issue.gl.manager import IssueGlManager
from tests.test_development.factories.gitlab import GlNoteFactory
from tests.test_development.test_gl.helpers import (
    gl_checkers,
    gl_mock,
    initializers,
)
from tests.test_users.factories.gitlab import GlUserFactory


def test_load_issue_notes(db, gl_mocker, gl_client):
    project, gl_project = initializers.init_project()
    issue, gl_issue = initializers.init_issue(project, gl_project)
    gl_author = GlUserFactory.create()
    gl_note = GlNoteFactory.create(
        author=gl_author, body="added 1h of time spent at 2000-01-01",
    )

    gl_mock.register_user(gl_mocker, gl_author)
    gl_mock.mock_project_endpoints(gl_mocker, gl_project)
    gl_mock.mock_issue_endpoints(
        gl_mocker, gl_project, gl_issue, notes=[gl_note],
    )

    gl_project = gl_client.projects.get(id=project.gl_id)
    gl_issue = gl_project.issues.get(id=issue.gl_iid)

    IssueGlManager().sync_notes(issue, gl_issue)

    note = issue.notes.first()

    assert note.gl_id == gl_note["id"]
    assert note.type == NoteType.TIME_SPEND
    assert note.body == "added 1h of time spent at 2000-01-01"
    assert note.created_at is not None
    assert note.updated_at is not None
    assert note.user.login == gl_author["username"]
    assert note.content_object == issue
    assert note.data == {"date": "2000-01-01", "spent": 3600}

    gl_checkers.check_user(note.user, gl_author)
