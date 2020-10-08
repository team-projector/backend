from typing import Dict, List, Optional

from apps.development.models.note import NoteType
from apps.development.services.extractors import (
    extract_issue_links,
    extract_tickets_links,
)
from apps.development.services.note.gl.parsers.base import (
    BaseNoteParser,
    NoteReadResult,
)


class CommentParser(BaseNoteParser):
    """Comment parser."""

    def parse(self, gl_note, work_item) -> Optional[NoteReadResult]:
        """Parse note."""
        is_system = getattr(gl_note, "system", False)  # noqa: WPS425
        if is_system:
            return None

        note_data: Dict[str, List[str]] = {}
        self._extract_issues(gl_note, work_item, note_data)
        self._extract_tickets(gl_note, note_data)

        if note_data:
            return NoteReadResult(NoteType.COMMENT, note_data)

        return None

    def _extract_issues(self, gl_note, work_item, note_data) -> None:
        """
        Extract issues.

        :param gl_note:
        :param work_item:
        :param note_data:
        :rtype: None
        """
        issues = extract_issue_links(gl_note.body, work_item)
        if issues:
            note_data["issues"] = issues

    def _extract_tickets(self, gl_note, note_data) -> None:
        """
        Extract tickets.

        :param gl_note:
        :param note_data:
        :rtype: None
        """
        tickets = extract_tickets_links(gl_note.body)
        if tickets:
            note_data["tickets"] = tickets
