# -*- coding: utf-8 -*-

from typing import Optional

from django.db import models

from apps.core.gitlab.parsers import parse_gl_datetime


class NoteManager(models.Manager):
    """The note model manager."""

    def update_from_gitlab(self, gl_note, issue) -> Optional[models.Model]:
        """Parse note and save from Gitlab."""
        from apps.development.services.note.gitlab import (  # noqa: WPS433
            read_note,
        )
        from apps.users.services.user.gl.manager import (  # noqa: WPS433
            UserGlManager,
        )

        if self._notes_are_synced(gl_note, issue):
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
            user=UserGlManager().extract_user_from_data(gl_note.author),
            content_object=issue,
            data=parse_data.data,
        )

    def _notes_are_synced(self, gl_note, issue) -> bool:
        last_date = issue.last_note_date
        return last_date and last_date > parse_gl_datetime(gl_note.created_at)
