# -*- coding: utf-8 -*-

from gitlab.v4.objects import ProjectIssue as GlProjectIssue

from apps.development.models import Issue
from apps.users.models import User

from ..users import load_user


def load_issue_participants(
    issue: Issue,
    gl_issue: GlProjectIssue,
) -> None:
    """Load participants for issue."""
    issue.participants.set((
        _get_user(user['id'])
        for user in gl_issue.participants()
    ))


def _get_user(gl_id: int) -> User:
    return User.objects.filter(gl_id=gl_id).first() or load_user(gl_id)
