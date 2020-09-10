# -*- coding: utf-8 -*-
from urllib3.exceptions import ReadTimeoutError

from apps.development.models import Project, ProjectGroup
from apps.development.services.milestone.gl.manager import MilestoneGlManager
from celery_app import app


@app.task(queue="low_priority", throws=(ReadTimeoutError,))
def sync_groups_milestones_task() -> None:
    """Syncing milestones in groups."""
    groups = ProjectGroup.objects.all()

    for project_group_id in groups.values_list("id", flat=True):
        sync_project_group_milestones_task.delay(project_group_id)


@app.task(queue="low_priority", throws=(ReadTimeoutError,))
def sync_projects_milestones_task() -> None:
    """Syncing milestones in projects."""
    for project_id in Project.objects.all().values_list("id", flat=True):
        sync_project_milestones_task.delay(project_id)


@app.task(queue="low_priority", throws=(ReadTimeoutError,))
def sync_project_group_milestones_task(project_group_id: int) -> None:
    """Load milestones for group."""
    group = ProjectGroup.objects.get(id=project_group_id)
    MilestoneGlManager().sync_project_group_milestones(group)


@app.task(throws=(ReadTimeoutError,))
def sync_project_group_milestone_task(
    group_id: int, milestone_id: int,
) -> None:
    """Syncing milestone in a group."""
    group = ProjectGroup.objects.get(gl_id=group_id)
    MilestoneGlManager().sync_project_group_milestone(group, milestone_id)


@app.task(queue="low_priority", throws=(ReadTimeoutError,))
def sync_project_milestones_task(project_id: int) -> None:
    """Load milestones for project."""
    project = Project.objects.get(id=project_id)
    MilestoneGlManager().sync_project_milestones(project)


@app.task(throws=(ReadTimeoutError,))
def sync_project_milestone_task(project_id: int, milestone_id: int) -> None:
    """Syncing milestone in a project."""
    project = Project.objects.get(gl_id=project_id)
    MilestoneGlManager().sync_project_milestone(project, milestone_id)
