from celery_app import app
from ..services.gitlab.groups import load_groups
from ..services.gitlab.projects import load_projects
from .milestones import sync_groups_milestones, sync_projects_milestones
from .issues import sync_issues
from .merge_requests import sync_merge_requests


@app.task(queue='low_priority')
def sync() -> None:
    load_groups()
    sync_groups_milestones.delay()

    load_projects()
    sync_projects_milestones.delay()
    sync_issues.delay()
    sync_merge_requests.delay()
