from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from celery_app import app
from ..models import Project
from ..services.gitlab.merge_requests import (
    load_project_merge_request, load_project_merge_requests,
)


@app.task(queue='low_priority')
def sync_merge_requests() -> None:
    for project_id in Project.objects.values_list('id', flat=True):
        sync_project_merge_requests.delay(project_id)


@app.task(queue='low_priority')
def sync_project_merge_requests(project_id: int) -> None:
    project = Project.objects.get(id=project_id)
    load_project_merge_requests(project)


@app.task
def sync_project_merge_request(project_id: int, iid: int) -> None:
    project = Project.objects.get(gl_id=project_id)

    gl = get_gitlab_client()
    gl_project = gl.projects.get(project_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    gl_merge_request = gl_project.mergerequests.get(iid)

    load_project_merge_request(project, gl_project, gl_merge_request)
