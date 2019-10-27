# -*- coding: utf-8 -*-

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from apps.development.models import ProjectGroup
from apps.development.services.project.gitlab import load_project
from apps.development.tasks import load_project_milestones
from celery_app import app


@app.task
def sync_project(group_id: int, gl_id: int, project_id: int) -> None:
    """Syncing project from Gitlab."""
    gl = get_gitlab_client()
    gl_project = gl.projects.get(gl_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    group = ProjectGroup.objects.get(id=group_id)

    load_project(gl, group, gl_project)
    load_project_milestones(project_id)
