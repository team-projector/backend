# -*- coding: utf-8 -*-

import re
import types
from collections import defaultdict, namedtuple
from functools import partial
from typing import DefaultDict, Optional, Pattern

from apps.core.gitlab.parsers import parse_gl_date, parse_gl_datetime
from apps.core.utils.time import seconds
from apps.development.models.note import NOTE_TYPES

RE_SPEND_FULL: Pattern = re.compile(
    r'^(?P<action>(added|subtracted)) (?P<spent>.+) '
    + r'of time spent at (?P<date>\d{4}-\d{2}-\d{2})$',
)
RE_SPEND_SHORT: Pattern = re.compile(
    r'^(?P<action>(added|subtracted)) (?P<spent>.+) of time spent$',
)
RE_SPEND_PART: Pattern = re.compile(r'(?P<value>\d+)(?P<part>(mo|w|d|h|m|s))')

SPEND_RESET_MESSAGE = 'removed time spent'

RE_MOVED_FROM: Pattern = re.compile(r'^moved from .+#\d+$')

WEEK_PER_MONTH = 4
DAYS_PER_WEEK = 5
HOURS_PER_DAY = 8
HOURS_PER_WEEK = DAYS_PER_WEEK * HOURS_PER_DAY
HOURS_PER_MONTH = WEEK_PER_MONTH * HOURS_PER_WEEK


def spend_handler_helper(
    bag: DefaultDict[str, int],
    time_value: int,
    key: str,
    multiplier: int = 1,
):
    """Helps to handle different units of time via multiplier."""
    bag[key] += time_value * multiplier


hours_helper = partial(spend_handler_helper, key='hours')

GITLAB_SPEND_HANDLERS = types.MappingProxyType({
    'mo': partial(hours_helper, multiplier=HOURS_PER_MONTH),
    'w': partial(hours_helper, multiplier=HOURS_PER_WEEK),
    'd': partial(hours_helper, multiplier=HOURS_PER_DAY),
    'h': hours_helper,
    'm': partial(spend_handler_helper, key='minutes'),
    's': partial(spend_handler_helper, key='seconds'),
})

NoteReadResult = namedtuple('NoteReadResult', ['type', 'data'])


def parse_spend(spent: str) -> int:
    """Parse spent time."""
    # specs https://docs.gitlab.com/ee/workflow/time_tracking.html
    spent = spent or ''
    spent = spent.strip()

    if not spent:
        return 0

    bag: DefaultDict[str, int] = defaultdict(int)

    for part in spent.split(' '):
        match = RE_SPEND_PART.match(part)
        if not match:
            continue

        GITLAB_SPEND_HANDLERS[match.group('part')](
            bag,
            int(match.group('value')),
        )

    return int(seconds(**bag))


class BaseNoteParser:
    """A base class note parser."""

    def parse(
        self,
        gl_note,
    ) -> Optional[NoteReadResult]:
        """Method should be implemented."""
        raise NotImplementedError


class SpendAddedParser(BaseNoteParser):
    """Spend added parser."""

    def parse(
        self,
        gl_note,
    ) -> Optional[NoteReadResult]:
        """Parse note."""
        match = (
            RE_SPEND_FULL.match(gl_note.body) or  # noqa: W504
            RE_SPEND_SHORT.match(gl_note.body)
        )
        if not match:
            return None

        spent = parse_spend(match.group('spent'))
        if match.group('action') == 'subtracted':
            spent *= -1

        if match.lastgroup == 'date':
            date = parse_gl_date(match.group('date'))
        else:
            datetime = parse_gl_datetime(gl_note.created_at)
            date = datetime.date() if datetime is not None else None

        return NoteReadResult(
            NOTE_TYPES.TIME_SPEND, {
                'spent': spent,
                'date': date,
            },
        )


class SpendResetParser(BaseNoteParser):
    """Spend reset parser."""

    def parse(
        self,
        gl_note,
    ) -> Optional[NoteReadResult]:
        """Parse note."""
        if gl_note.body == SPEND_RESET_MESSAGE:
            return NoteReadResult(NOTE_TYPES.RESET_SPEND, {})


class MovedFromParser(BaseNoteParser):
    """Moved from parser."""

    def parse(
        self,
        gl_note,
    ) -> Optional[NoteReadResult]:
        """Parse note."""
        is_system = getattr(gl_note, 'system', False)  # noqa: WPS425
        if is_system and RE_MOVED_FROM.match(gl_note.body):
            return NoteReadResult(NOTE_TYPES.MOVED_FROM, {})


_notes_parsers = [
    SpendAddedParser(),
    SpendResetParser(),
    MovedFromParser(),
]


def read_note(gl_note) -> Optional[NoteReadResult]:
    """Read note."""
    for parser in _notes_parsers:
        parse_data = parser.parse(gl_note)
        if parse_data:
            return parse_data
