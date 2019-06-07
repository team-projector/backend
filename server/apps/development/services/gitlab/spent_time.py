import logging

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.gitlab.gl_time import gl_duration
from apps.core.tasks import add_action

logger = logging.getLogger(__name__)


def add_spent_time(project_id: int,
                   issue_id: int,
                   seconds: int) -> None:
    gl = get_gitlab_client()
    gl_project = gl.projects.get(project_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    gl_issue = gl_project.issues.get(issue_id)

    gl_issue.add_spent_time(duration=gl_duration(seconds))
