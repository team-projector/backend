# -*- coding: utf-8 -*-

import re
from typing import Optional, Pattern

from apps.development.models.note import NoteType
from apps.development.services.note.gl.parsers.base import (
    BaseNoteParser,
    NoteReadResult,
)

RE_MOVED_FROM: Pattern[str] = re.compile(r"^moved from .+#\d+$")


class MovedFromParser(BaseNoteParser):
    """Moved from parser."""

    def parse(self, gl_note, work_item) -> Optional[NoteReadResult]:
        """Parse note."""
        is_system = getattr(gl_note, "system", False)  # noqa: WPS425
        if is_system and RE_MOVED_FROM.match(gl_note.body):
            return NoteReadResult(NoteType.MOVED_FROM, {})

        return None
