# -*- coding: utf-8 -*-

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.gitlab.gl_time import gl_duration
from apps.core.tasks import add_action
from apps.development.models import Issue
from apps.users.models import User


def add_spent_time(user: User,
                   issue: Issue,
                   seconds: int) -> None:
    gl = get_gitlab_client(user.gl_token)

    gl_project = gl.projects.get(issue.project.gl_id)
    gl_issue = gl_project.issues.get(issue.gl_iid)

    gl_issue.add_spent_time(duration=gl_duration(seconds))

    add_action.delay(verb=ACTION_GITLAB_CALL_API)
