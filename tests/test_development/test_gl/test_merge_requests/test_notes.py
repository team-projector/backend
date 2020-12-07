from apps.development.models.note import NoteType
from apps.development.services.merge_request.gl.manager import (
    MergeRequestGlManager,
)
from tests.helpers.checkers import assert_instance_fields
from tests.test_development.factories.gitlab import GlNoteFactory
from tests.test_development.test_gl.helpers import (
    gl_checkers,
    gl_mock,
    initializers,
)
from tests.test_users.factories.gitlab import GlUserFactory


def test_notes(db, gl_mocker, gl_client):
    """
    Test notes.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    project, gl_project = initializers.init_project()
    merge_request, gl_merge_request = initializers.init_merge_request(
        project,
        gl_project,
    )
    gl_author = GlUserFactory.create()
    gl_note = GlNoteFactory.create(
        author=gl_author,
        body="added 1h of time spent at 2000-01-01",
    )

    gl_mock.register_user(gl_mocker, gl_author)
    gl_mock.mock_project_endpoints(gl_mocker, gl_project)
    gl_mock.mock_merge_request_endpoints(
        gl_mocker,
        gl_project,
        gl_merge_request,
        notes=[gl_note],
    )

    gl_project = gl_client.projects.get(id=project.gl_id)
    gl_merge_request = gl_project.mergerequests.get(id=merge_request.gl_iid)

    MergeRequestGlManager().sync_notes(merge_request, gl_merge_request)

    note = merge_request.notes.first()

    assert note.created_at is not None
    assert note.updated_at is not None

    assert_instance_fields(
        note,
        gl_id=gl_note["id"],
        type=NoteType.TIME_SPEND,
        body="added 1h of time spent at 2000-01-01",
        content_object=merge_request,
        data={"date": "2000-01-01", "spent": 3600},
    )
    assert_instance_fields(note.user, login=gl_author["username"])

    gl_checkers.check_user(note.user, gl_author)
