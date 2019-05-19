import logging

from django.contrib.contenttypes.models import ContentType

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from .parsers import parse_gl_date, parse_gl_datetime
from ...models import Milestone, Project, ProjectGroup

logger = logging.getLogger(__name__)


def load_group_milestones(project_group_id: int,
                          gl_group_id: int) -> None:
    gl = get_gitlab_client()
    group = gl.groups.get(gl_group_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    for gl_milestone in group.milestones.list():
        Milestone.objects.sync_gitlab(
            gl_id=gl_milestone.id,
            gl_iid=gl_milestone.iid,
            gl_url=gl_milestone.web_url,
            title=gl_milestone.title,
            description=gl_milestone.description,
            content_type=ContentType.objects.get_for_model(ProjectGroup),
            object_id=project_group_id,
            start_date=parse_gl_date(gl_milestone.start_date),
            due_date=parse_gl_date(gl_milestone.due_date),
            created_at=parse_gl_datetime(gl_milestone.created_at),
            updated_at=parse_gl_datetime(gl_milestone.updated_at)
        )


def load_gl_project_milestones(project_id: int,
                               gl_project_id: int) -> None:
    gl = get_gitlab_client()
    gl_project = gl.projects.get(gl_project_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    for gl_milestone in gl_project.milestones.list():
        Milestone.objects.sync_gitlab(
            gl_id=gl_milestone.id,
            gl_iid=gl_milestone.iid,
            gl_url=gl_milestone.web_url,
            title=gl_milestone.title,
            description=gl_milestone.description,
            content_type=ContentType.objects.get_for_model(Project),
            object_id=project_id,
            start_date=parse_gl_date(gl_milestone.start_date),
            due_date=parse_gl_date(gl_milestone.due_date),
            created_at=parse_gl_datetime(gl_milestone.created_at),
            updated_at=parse_gl_datetime(gl_milestone.updated_at)
        )
