# -*- coding: utf-8 -*-

import re
from typing import Match, Optional, Pattern

from apps.core.gitlab.parsers import parse_gl_date, parse_gl_datetime
from apps.development.models.note import NoteType
from apps.development.services.note.gl.parsers.base import (
    BaseNoteParser,
    NoteReadResult,
    parse_spend,
)

RE_SPEND_FULL: Pattern[str] = re.compile(
    r"^(?P<action>(added|subtracted)) (?P<spent>.+) "
    + r"of time spent at (?P<date>\d{4}-\d{2}-\d{2})$",
)
RE_SPEND_SHORT: Pattern[str] = re.compile(
    r"^(?P<action>(added|subtracted)) (?P<spent>.+) of time spent$",
)


class SpendAddedParser(BaseNoteParser):
    """Spend added parser."""

    def parse(self, gl_note, work_item) -> Optional[NoteReadResult]:
        """Parse note."""
        match = RE_SPEND_FULL.match(
            gl_note.body,
        ) or RE_SPEND_SHORT.match(  # noqa: W504
            gl_note.body,
        )
        if not match:
            return None

        spent = parse_spend(match.group("spent"))
        if match.group("action") == "subtracted":
            spent *= -1

        return NoteReadResult(
            NoteType.TIME_SPEND,
            {"spent": spent, "date": self._extract_date(gl_note, match)},
        )

    def _extract_date(self, gl_note, match: Match[str]):
        if match.lastgroup == "date":
            return parse_gl_date(match.group("date"))

        datetime = parse_gl_datetime(gl_note.created_at)
        return datetime.date() if datetime is not None else None
