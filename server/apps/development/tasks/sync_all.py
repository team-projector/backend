# -*- coding: utf-8 -*-

from constance import config
from urllib3.exceptions import ReadTimeoutError

from apps.development.services.project.gl.manager import ProjectGlManager
from apps.development.services.project_group.gl.manager import (
    ProjectGroupGlManager,
)
from apps.development.tasks.issues import sync_issues_task
from apps.development.tasks.merge_requests import sync_merge_requests_task
from apps.development.tasks.milestones import (
    sync_groups_milestones_task,
    sync_projects_milestones_task,
)
from celery_app import app


@app.task(queue="low_priority", throws=(ReadTimeoutError,))
def sync_all_task() -> None:
    """Syncing everything."""
    if not config.GITLAB_SYNC:
        return

    ProjectGroupGlManager().sync_all_groups()
    sync_groups_milestones_task()

    ProjectGlManager().sync_all_projects()
    sync_projects_milestones_task()

    sync_issues_task()
    sync_merge_requests_task()
