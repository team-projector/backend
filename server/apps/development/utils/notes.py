import re
from collections import namedtuple
from typing import Optional, Pattern

from .parsers import parse_spend

RE_SPEND: Pattern = re.compile(r'^(?P<action>(added|subtracted)) (?P<spent>.+) of time spent at \d{4}-\d{2}-\d{2}$')
SPEND_RESET_MESSAGE = 'removed time spent'

NoteReadResult = namedtuple('NoteReadResult', ['type', 'data'])


class BaseNoteParser:
    def parse(self, gl_note) -> Optional[NoteReadResult]:
        raise NotImplementedError


class SpendAddedParser(BaseNoteParser):
    def parse(self, gl_note) -> Optional[NoteReadResult]:
        from ..models import Note

        m = RE_SPEND.match(gl_note.body)
        if not m:
            return

        spent = parse_spend(m.group('spent'))
        if m.group('action') == 'subtracted':
            spent *= -1

        return NoteReadResult(
            Note.TYPE.time_spend, {
                'spent': spent
            }
        )


class SpendResetParser(BaseNoteParser):
    def parse(self, gl_note) -> Optional[NoteReadResult]:
        from ..models import Note

        if gl_note.body == SPEND_RESET_MESSAGE:
            return NoteReadResult(Note.TYPE.reset_spend, {})


NOTES_PARSERS = [
    SpendAddedParser(),
    SpendResetParser()
]


def read_note(gl_note) -> Optional[NoteReadResult]:
    for parser in NOTES_PARSERS:
        parse_data = parser.parse(gl_note)
        if parse_data:
            return parse_data
