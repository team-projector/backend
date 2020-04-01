# -*- coding: utf-8 -*-

from typing import Optional

from apps.development.models.note import NoteType
from apps.development.services.note.notes_parsers.base import (
    RE_MOVED_FROM,
    BaseNoteParser,
    NoteReadResult,
)


class MovedFromParser(BaseNoteParser):
    """Moved from parser."""

    def parse(self, gl_note) -> Optional[NoteReadResult]:
        """Parse note."""
        is_system = getattr(gl_note, "system", False)  # noqa: WPS425
        if is_system and RE_MOVED_FROM.match(gl_note.body):
            return NoteReadResult(NoteType.MOVED_FROM, {})

        return None
