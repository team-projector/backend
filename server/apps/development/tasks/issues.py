# -*- coding: utf-8 -*-

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from celery_app import app

from ..models import Project
from ..services.gitlab.issues import load_project_issue, load_project_issues


@app.task(queue='low_priority')
def sync_issues() -> None:
    """Syncing issues from Gitlab."""
    for project_id in Project.objects.values_list('id', flat=True):
        sync_project_issues.delay(project_id)


@app.task(queue='low_priority')
def sync_project_issues(project_id: int) -> None:
    """Syncing issues for project from Gitlab."""
    project = Project.objects.get(id=project_id)
    load_project_issues(project)


@app.task
def sync_project_issue(project_id: int, iid: int) -> None:
    """Syncing issue for project from Gitlab."""
    project = Project.objects.get(gl_id=project_id)

    gl = get_gitlab_client()
    gl_project = gl.projects.get(project_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    gl_issue = gl_project.issues.get(iid)

    load_project_issue(project, gl_project, gl_issue)
