# -*- coding: utf-8 -*-

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from apps.development.models import Project
from apps.development.services import issue as issue_service
from celery_app import app


@app.task(queue='low_priority')
def sync_issues() -> None:
    """Syncing issues from Gitlab."""
    for project_id in Project.objects.values_list('id', flat=True):
        sync_project_issues.delay(project_id)


@app.task(queue='low_priority')
def sync_project_issues(project_id: int) -> None:
    """Syncing issues for project from Gitlab."""
    project = Project.objects.get(id=project_id)
    issue_service.load_for_project_all(project)


@app.task
def sync_project_issue(project_id: int, iid: int) -> None:
    """Syncing issue for project from Gitlab."""
    project = Project.objects.get(gl_id=project_id)

    gl = get_gitlab_client()
    gl_project = gl.projects.get(project_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    gl_issue = gl_project.issues.get(iid)

    issue_service.load_for_project(project, gl_project, gl_issue)
