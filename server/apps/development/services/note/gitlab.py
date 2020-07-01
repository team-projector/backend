# -*- coding: utf-8 -*-

from typing import Optional

from apps.development.services.note.gl.parsers import (
    CommentParser,
    MovedFromParser,
    SpendAddedParser,
    SpendResetParser,
)
from apps.development.services.note.gl.parsers.base import NoteReadResult

_notes_parsers = [
    SpendAddedParser(),
    SpendResetParser(),
    MovedFromParser(),
    CommentParser(),
]


def read_note(gl_note) -> Optional[NoteReadResult]:
    """Read note."""
    for parser in _notes_parsers:
        parse_data = parser.parse(gl_note)
        if parse_data:
            return parse_data

    return None
