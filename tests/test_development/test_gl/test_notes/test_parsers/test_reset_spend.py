from datetime import datetime

from jnt_django_toolbox.helpers.objects import dict2obj

from apps.core.gitlab import GITLAB_DATETIME_FORMAT
from apps.development.models import Note
from apps.development.models.note import NoteType
from apps.development.services.note.gl.parsers.spend_reset import (
    SPEND_RESET_MESSAGE,
)
from apps.development.services.note.gl.sync import update_note_from_gitlab
from tests.helpers.checkers import assert_instance_fields
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

    assert not note.data
    assert_instance_fields(
        note,
        gl_id=2,
        user=user,
        body=SPEND_RESET_MESSAGE,
        type=NoteType.RESET_SPEND,
    )
