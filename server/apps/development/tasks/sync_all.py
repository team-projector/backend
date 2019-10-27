# -*- coding: utf-8 -*-

from apps.development.services.project.gitlab import load_projects
from apps.development.services.project_group.gitlab import load_groups
from apps.development.tasks.issues import sync_issues
from apps.development.tasks.merge_requests import sync_merge_requests
from apps.development.tasks.milestones import (
    sync_groups_milestones,
    sync_projects_milestones,
)
from celery_app import app


@app.task(queue='low_priority')
def sync() -> None:
    """Syncing everything."""
    load_groups()
    sync_groups_milestones.delay()

    load_projects()
    sync_projects_milestones.delay()
    sync_issues.delay()
    sync_merge_requests.delay()
