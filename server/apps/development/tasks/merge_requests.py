# -*- coding: utf-8 -*-
from urllib3.exceptions import ReadTimeoutError

from apps.development.models import Project
from apps.development.services.merge_request.gl.manager import (
    MergeRequestGlManager,
)
from apps.development.services.project.gl.provider import ProjectGlProvider
from celery_app import app


@app.task(queue="low_priority", throws=(ReadTimeoutError,))
def sync_merge_requests_task() -> None:
    """Syncing merge requests for all projects from Gitlab."""
    for project_id in Project.objects.values_list("id", flat=True):
        sync_project_merge_requests_task.delay(project_id)


@app.task(queue="low_priority", throws=(ReadTimeoutError,))
def sync_project_merge_requests_task(project_id: int) -> None:
    """Syncing merge requests for project from Gitlab."""
    project = Project.objects.get(id=project_id)

    manager = MergeRequestGlManager()
    manager.sync_project_merge_requests(project)


@app.task(throws=(ReadTimeoutError,))
def sync_project_merge_request_task(project_id: int, iid: int) -> None:
    """Syncing merge request for project from Gitlab."""
    project = Project.objects.get(gl_id=project_id)

    project_provider = ProjectGlProvider()
    gl_project = project_provider.get_gl_project(project)
    if not gl_project:
        return

    manager = MergeRequestGlManager()
    manager.update_merge_request(
        project, gl_project, gl_project.mergerequests.get(iid),
    )
