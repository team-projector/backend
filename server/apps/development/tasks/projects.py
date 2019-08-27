from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from celery_app import app
from ..models import ProjectGroup
from ..services.gitlab.projects import load_project
from .milestones import load_project_milestones


@app.task
def sync_project(group_id: int, gl_id: int, project_id: int) -> None:
    gl = get_gitlab_client()
    gl_project = gl.projects.get(gl_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    group = ProjectGroup.objects.get(id=group_id)

    load_project(gl, group, gl_project)
    load_project_milestones(project_id)
