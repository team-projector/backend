# -*- coding: utf-8 -*-

from typing import Optional

from apps.development.models.note import NoteType
from apps.development.services.note.gl.parsers.base import (
    BaseNoteParser,
    NoteReadResult,
)

SPEND_RESET_MESSAGE = "removed time spent"


class SpendResetParser(BaseNoteParser):
    """Spend reset parser."""

    def parse(self, gl_note, work_item) -> Optional[NoteReadResult]:
        """Parse note."""
        if gl_note.body == SPEND_RESET_MESSAGE:
            return NoteReadResult(NoteType.RESET_SPEND, {})

        return None
