# -*- coding: utf-8 -*-

from datetime import datetime

from apps.core.gitlab import GITLAB_DATETIME_FORMAT
from apps.core.utils.objects import dict2obj
from apps.development.models import Note
from apps.development.models.note import NOTE_TYPES
from apps.development.services.note.gitlab import SPEND_RESET_MESSAGE
from tests.test_development.factories import IssueFactory


def test_reset(user):
    issue = IssueFactory.create()

    Note.objects.update_from_gitlab(dict2obj({
        "id": 2,
        "body": SPEND_RESET_MESSAGE,
        "created_at": datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
        "updated_at": datetime.strftime(datetime.now(), GITLAB_DATETIME_FORMAT),
        "author": {
            "id": user.gl_id
        }
    }), issue)

    assert Note.objects.count() == 1

    note = Note.objects.first()
    assert note.gl_id == 2
    assert note.user == user
    assert note.body == SPEND_RESET_MESSAGE
    assert note.type == NOTE_TYPES.RESET_SPEND
    assert not note.data
