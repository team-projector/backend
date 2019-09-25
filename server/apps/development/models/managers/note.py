# -*- coding: utf-8 -*-

from typing import Any

from django.db import models


class NoteManager(models.Manager):
    def sync_gitlab(self, gl_note, issue) -> Any:
        from ...services.gitlab.users import extract_user_from_data
        from ...services.gitlab.notes import read_note
        from ...services.gitlab.parsers import parse_gl_datetime

        last_date = issue.last_note_date

        if last_date and last_date > parse_gl_datetime(gl_note.created_at):
            return None

        parse_data = read_note(gl_note)
        if not parse_data:
            return None

        note = issue.notes.filter(gl_id=gl_note.id).first()
        if note:
            return note

        return self.create(
            gl_id=gl_note.id,
            type=parse_data.type,
            body=gl_note.body,
            created_at=parse_gl_datetime(gl_note.created_at),
            updated_at=parse_gl_datetime(gl_note.updated_at),
            user=extract_user_from_data(gl_note.author),
            content_object=issue,
            data=parse_data.data,
        )
