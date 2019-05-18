import re
from collections import defaultdict, namedtuple
from datetime import timedelta
from typing import DefaultDict, Optional, Pattern

from apps.development.services.gitlab.parsers import parse_gl_date

RE_SPEND: Pattern = re.compile(
    r'^(?P<action>(added|subtracted)) (?P<spent>.+) of time spent at (?P<date>\d{4}-\d{2}-\d{2})$'
)
RE_SPEND_PART: Pattern = re.compile(r'(?P<value>\d+)(?P<part>(mo|w|d|h|m|s))')
SPEND_RESET_MESSAGE = 'removed time spent'

WEEK_PER_MONTH = 4
DAYS_PER_WEEK = 5
HOURS_PER_DAY = 8


def seconds_handler(bag: DefaultDict[str, int], val: int) -> None:
    bag['seconds'] += val


def minutes_handler(bag: DefaultDict[str, int], val: int) -> None:
    bag['minutes'] += val


def hours_handler(bag: DefaultDict[str, int],
                  val: int) -> None:
    bag['hours'] += val


def days_handler(bag: DefaultDict[str, int], val: int) -> None:
    bag['hours'] += val * HOURS_PER_DAY


def weeks_handler(bag: DefaultDict[str, int], val: int) -> None:
    bag['hours'] += val * DAYS_PER_WEEK * HOURS_PER_DAY


def months_handler(bag: DefaultDict[str, int], val: int) -> None:
    bag['hours'] += val * WEEK_PER_MONTH * DAYS_PER_WEEK * HOURS_PER_DAY


GITLAB_SPEND_HANDLERS = {
    'mo': months_handler,
    'w': weeks_handler,
    'd': days_handler,
    'h': hours_handler,
    'm': minutes_handler,
    's': seconds_handler
}

NoteReadResult = namedtuple('NoteReadResult', ['type', 'data'])


def parse_spend(s: str) -> int:
    # specs https://docs.gitlab.com/ee/workflow/time_tracking.html
    s = s or ''
    s = s.strip()

    if not s:
        return 0

    bag: DefaultDict[str, int] = defaultdict(int)

    for part in s.split(' '):
        m = RE_SPEND_PART.match(part)
        if not m:
            continue

        GITLAB_SPEND_HANDLERS[m.group('part')](bag, int(m.group('value')))

    return int(timedelta(**bag).total_seconds())


class BaseNoteParser:
    def parse(self, gl_note) -> Optional[NoteReadResult]:
        raise NotImplementedError


class SpendAddedParser(BaseNoteParser):
    def parse(self, gl_note) -> Optional[NoteReadResult]:
        from ...models import Note

        m = RE_SPEND.match(gl_note.body)
        if not m:
            return None

        spent = parse_spend(m.group('spent'))
        if m.group('action') == 'subtracted':
            spent *= -1

        return NoteReadResult(
            Note.TYPE.time_spend, {
                'spent': spent,
                'date': parse_gl_date(m.group('date'))
            }
        )


class SpendResetParser(BaseNoteParser):
    def parse(self, gl_note) -> Optional[NoteReadResult]:
        from ...models import Note

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