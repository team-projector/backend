# -*- coding: utf-8 -*-

from celery_app import app
from ..models import Project, ProjectGroup
from ..services.gitlab.milestones import (
    load_gl_project_milestones, load_group_milestone, load_group_milestones,
    load_project_milestone,
)


@app.task(queue='low_priority')
def sync_groups_milestones() -> None:
    groups = ProjectGroup.objects.all()

    for project_group_id in groups.values_list('id', flat=True):
        load_project_group_milestones.delay(project_group_id)


@app.task(queue='low_priority')
def sync_projects_milestones() -> None:
    for project_id in Project.objects.all().values_list('id', flat=True):
        load_project_milestones.delay(project_id)


@app.task(queue='low_priority')
def load_project_group_milestones(project_group_id: int) -> None:
    group = ProjectGroup.objects.get(id=project_group_id)
    load_group_milestones(project_group_id, group.gl_id)


@app.task(queue='low_priority')
def load_project_milestones(project_id: int) -> None:
    project = Project.objects.get(id=project_id)
    load_gl_project_milestones(project_id, project.gl_id)


@app.task
def sync_project_milestone(project_id: int, milestone_id: int) -> None:
    project = Project.objects.get(gl_id=project_id)
    load_project_milestone(project, project_id, milestone_id)


@app.task
def sync_group_milestone(group_id: int, milestone_id: int) -> None:
    group = ProjectGroup.objects.get(gl_id=group_id)
    load_group_milestone(group, group_id, milestone_id)
