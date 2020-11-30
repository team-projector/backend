from http import HTTPStatus

from constance import config
from gitlab import GitlabHttpError

from apps.core.gitlab.errors import sync_errors
from apps.development.models import Issue, Project
from apps.development.services.issue.gl.manager import IssueGlManager
from apps.development.services.issue.tickets.propagator import (
    propagate_ticket_to_related_issues,
)
from apps.development.services.project.gl.provider import ProjectGlProvider
from celery_app import app


@app.task(queue="low_priority", throws=sync_errors)
def sync_issues_task() -> None:
    """Syncing issues from Gitlab."""
    for project_id in Project.objects.values_list("id", flat=True):
        sync_project_issues_task.delay(project_id)


@app.task(queue="low_priority", throws=sync_errors)
def sync_project_issues_task(project_id: int) -> None:
    """Syncing issues for project from Gitlab."""
    project = Project.objects.get(id=project_id)

    manager = IssueGlManager()
    manager.sync_project_issues(
        project,
        start_date=config.GITLAB_SYNC_START_DATE or None,
    )


@app.task(throws=sync_errors)
def sync_project_issue_task(project_id: int, iid: int) -> None:
    """Syncing issue for project from Gitlab."""
    project = Project.objects.get(gl_id=project_id)

    project_provider = ProjectGlProvider()
    gl_project = project_provider.get_gl_project(project)
    if not gl_project:
        return

    manager = IssueGlManager()

    try:
        gl_issue = gl_project.issues.get(iid)
    except GitlabHttpError as err:
        if err.response_code != HTTPStatus.NOT_FOUND:
            raise
    else:
        manager.update_project_issue(project, gl_project, gl_issue)


@app.task
def propagate_ticket_to_related_issues_task(issue_id: int) -> None:
    """Propagate ticket from parent issues to child."""
    issue = Issue.objects.filter(id=issue_id).first()
    if issue:
        propagate_ticket_to_related_issues(issue)
