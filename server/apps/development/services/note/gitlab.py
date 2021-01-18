from typing import Optional

from apps.core.gitlab import get_gitlab_client
from apps.development.models import Issue
from apps.development.services.note.gl.parsers import (
    CommentParser,
    MovedFromParser,
    SpendAddedParser,
    SpendResetParser,
)
from apps.development.services.note.gl.parsers.base import NoteReadResult
from apps.users.models import User

_notes_parsers = [
    SpendAddedParser(),
    SpendResetParser(),
    MovedFromParser(),
    CommentParser(),
]


def read_note(gl_note, work_item) -> Optional[NoteReadResult]:
    """Read note."""
    for parser in _notes_parsers:
        parse_data = parser.parse(gl_note, work_item)
        if parse_data:
            return parse_data

    return None


def add_issue_note(user: User, issue: Issue, message: str) -> None:
    """Add note to issue."""
    gl = get_gitlab_client(user.gl_token)

    gl_project = gl.projects.get(issue.project.gl_id)
    gl_issue = gl_project.issues.get(issue.gl_iid)

    gl_issue.notes.create({"body": message})
