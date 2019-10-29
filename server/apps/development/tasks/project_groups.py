# -*- coding: utf-8 -*-

from apps.development.models import ProjectGroup
from apps.development.services.project_group.gl.manager import (
    ProjectGroupGlManager,
)
from apps.development.services.project_group.gl.provider import (
    ProjectGroupGlProvider,
)
from celery_app import app


@app.task
def sync_project_group_task(gl_id: int) -> None:
    """Syncing project group."""
    group = ProjectGroup.objects.get(gl_id=gl_id)

    project_group_provider = ProjectGroupGlProvider()
    gl_group = project_group_provider.get_gl_group(group)
    if not gl_group:
        return

    parent = None
    if gl_group.parent_id:
        parent = ProjectGroup.objects.get(gl_id=gl_group.parent_id)

    manager = ProjectGroupGlManager()
    manager.update_group(
        gl_group,
        parent,
    )
