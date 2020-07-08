# -*- coding: utf-8 -*-

from typing import Optional

from django.db import models

from apps.core.gitlab.parsers import parse_gl_datetime
from apps.development.models import Note
from apps.development.models.note import NoteType

IMMUTABLE_NOTES = (
    NoteType.MOVED_FROM,
    NoteType.RESET_SPEND,
    NoteType.TIME_SPEND,
)


def update_note_from_gitlab(gl_note, work_item) -> Optional[models.Model]:
    """Parse note and save from Gitlab."""
    from apps.development.services.note.gitlab import read_note  # noqa: WPS433
    from apps.users.services.user.gl.manager import (  # noqa: WPS433
        UserGlManager,
    )

    parse_data = read_note(gl_note, work_item)
    if not parse_data:
        return None

    note = work_item.notes.filter(gl_id=gl_note.id).first()
    if note:
        if note.type not in IMMUTABLE_NOTES:
            note.type = parse_data.type  # noqa: WPS125
            note.body = gl_note.body
            note.updated_at = parse_gl_datetime(gl_note.updated_at)
            note.data = parse_data.data  # noqa: WPS110
            note.save()
    else:
        note = Note.objects.create(
            gl_id=gl_note.id,
            type=parse_data.type,
            body=gl_note.body,
            created_at=parse_gl_datetime(gl_note.created_at),
            updated_at=parse_gl_datetime(gl_note.updated_at),
            user=UserGlManager().extract_user_from_data(gl_note.author),
            content_object=work_item,
            data=parse_data.data,
        )

    return note
