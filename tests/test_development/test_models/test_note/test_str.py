# -*- coding: utf-8 -*-

from apps.development.models.note import NOTE_TYPES
from tests.test_development.factories import IssueNoteFactory


def test_str(user):
    note = IssueNoteFactory.create(
        user=user,
        type=NOTE_TYPES.TIME_SPEND,
    )

    assert str(note) == "{0} [{1}]: Time spend".format(
        user.login,
        note.created_at,
    )
