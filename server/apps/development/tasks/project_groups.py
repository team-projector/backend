# -*- coding: utf-8 -*-

from apps.core.activity.verbs import ACTION_GITLAB_CALL_API
from apps.core.gitlab import get_gitlab_client
from apps.core.tasks import add_action
from apps.development.models import ProjectGroup
from apps.development.services.project_group.gitlab import load_single_group
from celery_app import app


@app.task
def sync_project_group(gl_id: int) -> None:
    """Syncing project group."""
    gl = get_gitlab_client()
    gl_group = gl.groups.get(id=gl_id)

    add_action.delay(verb=ACTION_GITLAB_CALL_API)

    parent = None
    if gl_group.parent_id:
        parent = ProjectGroup.objects.get(gl_id=gl_group.parent_id)

    load_single_group(gl_group, parent)
