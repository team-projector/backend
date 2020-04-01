# -*- coding: utf-8 -*-

from typing import Optional

from apps.development.models.note import NoteType
from apps.development.services.note.notes_parsers.base import (
    SPEND_RESET_MESSAGE,
    BaseNoteParser,
    NoteReadResult,
)


class SpendResetParser(BaseNoteParser):
    """Spend reset parser."""

    def parse(self, gl_note) -> Optional[NoteReadResult]:
        """Parse note."""
        if gl_note.body == SPEND_RESET_MESSAGE:
            return NoteReadResult(NoteType.RESET_SPEND, {})

        return None
