# -*- coding: utf-8 -*-

from datetime import datetime

from jnt_django_toolbox.helpers.objects import dict2obj

from apps.core.gitlab import GITLAB_DATETIME_FORMAT
from apps.development.models import Note
from apps.development.models.note import NoteType
from apps.development.services.note.gl.parsers.spend_reset import (
    SPEND_RESET_MESSAGE,
)
from apps.development.services.note.gl.sync import update_note_from_gitlab
from tests.test_development.factories import IssueFactory


def test_reset(user):
    """
    Test reset.

    :param user:
    """
    issue = IssueFactory.create()

    update_note_from_gitlab(
        dict2obj(
            {
                "id": 2,
                "body": SPEND_RESET_MESSAGE,
                "created_at": datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                "updated_at": datetime.strftime(
                    datetime.now(),
                    GITLAB_DATETIME_FORMAT,
                ),
                "author": {"id": user.gl_id},
            },
        ),
        issue,
    )

    assert Note.objects.count() == 1

    note = Note.objects.first()
    assert note.gl_id == 2
    assert note.user == user
    assert note.body == SPEND_RESET_MESSAGE
    assert note.type == NoteType.RESET_SPEND
    assert not note.data
