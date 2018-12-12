from celery import chain

from apps.development.models import Project
from apps.development.utils.loaders import load_groups, load_project_issues, load_projects
from celery_app import app


@app.task
def sync() -> None:
    chain(sync_groups.s(), sync_projects.s(), sync_issues.s())()


@app.task
def sync_groups() -> None:
    load_groups()


@app.task
def sync_projects() -> None:
    load_projects()


@app.task
def sync_issues() -> None:
    for project_id in Project.objects.values_list('id', flat=True):
        sync_project_issues.delay(project_id)


@app.task
def sync_project_issues(project_id: int) -> None:
    project = Project.objects.get(id=project_id)
    load_project_issues(project)
