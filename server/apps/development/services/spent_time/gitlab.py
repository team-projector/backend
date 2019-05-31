import logging
import time

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action

logger = logging.getLogger(__name__)

GITLAB_SPEND_TIME_FORMAT = '%-Hh%-Mm'


def gl_time_spend_format(seconds: int) -> str:
    # TODO: reset is negative seconds?
    return time.strftime(GITLAB_SPEND_TIME_FORMAT, time.gmtime(seconds)) if seconds > 0 else ''


def add_spent_time(project_id: int,
                   issue_id: int,
                   duration: int) -> None:
    gl = get_gitlab_client()
    gl_project = gl.projects.get(project_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    gl_issue = gl_project.issues.get(issue_id)

    gl_issue.add_spent_time(gl_time_spend_format(duration))
