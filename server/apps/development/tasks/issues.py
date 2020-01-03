# -*- coding: utf-8 -*-

from apps.development.models import Project
from apps.development.services.issue.gl.manager import IssueGlManager
from apps.development.services.project.gl.provider import ProjectGlProvider
from celery_app import app


@app.task(queue="low_priority")
def sync_issues_task() -> None:
    """Syncing issues from Gitlab."""
    for project_id in Project.objects.values_list("id", flat=True):
        sync_project_issues_task.delay(project_id)


@app.task(queue="low_priority")
def sync_project_issues_task(project_id: int) -> None:
    """Syncing issues for project from Gitlab."""
    project = Project.objects.get(id=project_id)

    manager = IssueGlManager()
    manager.sync_project_issues(project)


@app.task
def sync_project_issue_task(project_id: int, iid: int) -> None:
    """Syncing issue for project from Gitlab."""
    project = Project.objects.get(gl_id=project_id)

    project_provider = ProjectGlProvider()
    gl_project = project_provider.get_gl_project(project)
    if not gl_project:
        return

    manager = IssueGlManager()
    manager.update_project_issue(
        project,
        gl_project,
        gl_project.issues.get(iid),
    )
