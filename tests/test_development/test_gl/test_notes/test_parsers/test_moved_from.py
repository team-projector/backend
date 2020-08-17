# -*- coding: utf-8 -*-

from datetime import datetime

from jnt_django_toolbox.helpers.objects import dict2obj

from apps.core.gitlab import GITLAB_DATETIME_FORMAT
from apps.development.models import Note
from apps.development.models.note import NoteType
from apps.development.services.note.gl.sync import update_note_from_gitlab
from tests.test_development.factories import IssueFactory


def test_success(user):
    """
    Test success.

    :param user:
    """
    issue = IssueFactory.create()

    body = "moved from group/project#111"

    update_note_from_gitlab(
        dict2obj(
            {
                "id": 2,
                "body": body,
                "created_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "updated_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "author": {"id": user.gl_id},
                "system": True,
            },
        ),
        issue,
    )

    assert Note.objects.count() == 1

    note = Note.objects.first()
    assert note.gl_id == 2
    assert note.user == user
    assert note.type == NoteType.MOVED_FROM
    assert note.body == body


def test_no_system(user):
    """
    Test no system.

    :param user:
    """
    issue = IssueFactory.create()

    body = "moved from group/project#111"

    update_note_from_gitlab(
        dict2obj(
            {
                "id": 2,
                "body": body,
                "created_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "updated_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "author": {"id": user.gl_id},
                "system": False,
            },
        ),
        issue,
    )

    assert not Note.objects.exists()


def test_bad_issue_number(user):
    """
    Test bad issue number.

    :param user:
    """
    issue = IssueFactory.create()

    body = "moved from group/project#111b"

    update_note_from_gitlab(
        dict2obj(
            {
                "id": 2,
                "body": body,
                "created_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "updated_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "author": {"id": user.gl_id},
                "system": True,
            },
        ),
        issue,
    )

    assert not Note.objects.exists()
