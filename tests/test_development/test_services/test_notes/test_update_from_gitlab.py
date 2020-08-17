# -*- coding: utf-8 -*-

from jnt_django_toolbox.helpers.objects import dict2obj

from apps.development.models.note import NoteType
from apps.development.services.note.gl.sync import update_note_from_gitlab
from tests.test_development.factories import IssueFactory
from tests.test_development.factories.gitlab import GlNoteFactory
from tests.test_development.test_gl.helpers import gl_mock
from tests.test_users.factories.gitlab import GlUserFactory


def test_load_new(db, gl_mocker, gl_client):
    """
    Test load new.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    gl_author = GlUserFactory.create()
    gl_mock.register_user(gl_mocker, gl_author)
    gl_note = GlNoteFactory.create(
        author=gl_author, body="added 1h of time spent at 2000-01-01",
    )
    issue = IssueFactory.create()

    update_note_from_gitlab(dict2obj(gl_note), issue)

    note = issue.notes.first()

    assert note.gl_id == gl_note["id"]
    assert note.type == NoteType.TIME_SPEND
    assert note.body == "added 1h of time spent at 2000-01-01"
    assert note.created_at is not None
    assert note.updated_at is not None
    assert note.content_object == issue
    assert note.data == {"date": "2000-01-01", "spent": 3600}


def test_update_immutable(db, gl_mocker, gl_client):
    """
    Test update immutable.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    gl_author = GlUserFactory.create()
    gl_mock.register_user(gl_mocker, gl_author)
    gl_note = GlNoteFactory.create(
        author=gl_author, body="added 1h of time spent at 2000-01-01",
    )
    issue = IssueFactory.create()

    update_note_from_gitlab(dict2obj(gl_note), issue)

    gl_note["body"] = "added 5h of time spent at 2000-01-01"
    update_note_from_gitlab(dict2obj(gl_note), issue)
    note = issue.notes.first()

    assert note.gl_id == gl_note["id"]
    assert note.type == NoteType.TIME_SPEND
    assert note.body == "added 1h of time spent at 2000-01-01"
    assert note.data == {"date": "2000-01-01", "spent": 3600}


def test_update_mutable(db, gl_mocker, gl_client):
    """
    Test update mutable.

    :param db:
    :param gl_mocker:
    :param gl_client:
    """
    gl_author = GlUserFactory.create()
    gl_mock.register_user(gl_mocker, gl_author)

    links = [
        "https://gitlab.com/junte/esanum/social/backend/-/issues/3510",
        "https://gitlab.com/junte/esanum/social/backend/-/issues/3511",
    ]
    gl_note = GlNoteFactory.create(
        author=gl_author, body="link {0}".format(links[0]),
    )
    issue = IssueFactory.create()

    update_note_from_gitlab(dict2obj(gl_note), issue)

    note = issue.notes.first()
    assert note.type == NoteType.COMMENT
    assert note.data.get("issues") == [links[0]]

    gl_note["body"] = "link {0}".format(links[1])
    update_note_from_gitlab(dict2obj(gl_note), issue)

    note = issue.notes.first()
    assert note.type == NoteType.COMMENT
    assert note.data.get("issues") == [links[1]]
