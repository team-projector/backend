# -*- coding: utf-8 -*-

from typing import Match, Optional

from apps.core.gitlab.parsers import parse_gl_date, parse_gl_datetime
from apps.development.models.note import NoteType
from apps.development.services.note.notes_parsers.base import (
    RE_SPEND_FULL,
    RE_SPEND_SHORT,
    BaseNoteParser,
    NoteReadResult,
    parse_spend,
)


class SpendAddedParser(BaseNoteParser):
    """Spend added parser."""

    def parse(self, gl_note) -> Optional[NoteReadResult]:
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
