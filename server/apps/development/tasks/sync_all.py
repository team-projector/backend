# -*- coding: utf-8 -*-

from celery_app import app

from ..services.gitlab.groups import load_groups
from ..services.gitlab.projects import load_projects
from .issues import sync_issues
from .merge_requests import sync_merge_requests
from .milestones import sync_groups_milestones, sync_projects_milestones


@app.task(queue='low_priority')
def sync() -> None:
    """Syncing everything."""
    load_groups()
    sync_groups_milestones.delay()

    load_projects()
    sync_projects_milestones.delay()
    sync_issues.delay()
    sync_merge_requests.delay()
