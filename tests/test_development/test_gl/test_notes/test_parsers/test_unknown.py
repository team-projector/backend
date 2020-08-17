# -*- coding: utf-8 -*-

from datetime import datetime

from jnt_django_toolbox.helpers.objects import dict2obj

from apps.core.gitlab import GITLAB_DATETIME_FORMAT
from apps.development.models import Note
from apps.development.services.note.gl.sync import update_note_from_gitlab
from tests.test_development.factories import IssueFactory


def test_unsupported(user):
    """
    Test unsupported.

    :param user:
    """
    issue = IssueFactory.create()
    update_note_from_gitlab(
        dict2obj(
            {
                "id": 2,
                "body": "bla",
                "created_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "updated_at": datetime.strftime(
                    datetime.now(), GITLAB_DATETIME_FORMAT,
                ),
                "author": {"id": user.gl_id},
            },
        ),
        issue,
    )

    assert not Note.objects.exists()
