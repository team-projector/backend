# -*- coding: utf-8 -*-

from typing import List, Optional

from apps.development.models.note import NoteType
from apps.development.services.note.gl.parsers.base import (
    RE_GITLAB_ISSUE_LINK,
    RE_ISSUE_NUMBER,
    BaseNoteParser,
    NoteReadResult,
)


class CommentParser(BaseNoteParser):
    """Comment parser."""

    def parse(self, gl_note) -> Optional[NoteReadResult]:
        """Parse note."""
        is_system = getattr(gl_note, "system", False)  # noqa: WPS425

        if is_system:
            return None

        note_data = {}

        numbers = self._get_issue_numbers(gl_note)
        links = self._get_issue_links(gl_note)

        if numbers:
            note_data["numbers"] = numbers

        if links:
            note_data["links"] = links

        if note_data:
            return NoteReadResult(NoteType.COMMENT, note_data)

        return None

    def _get_issue_numbers(self, gl_note) -> List[str]:
        return [match[2] for match in RE_ISSUE_NUMBER.findall(gl_note.body)]

    def _get_issue_links(self, gl_note) -> List[str]:
        return RE_GITLAB_ISSUE_LINK.findall(gl_note.body)
