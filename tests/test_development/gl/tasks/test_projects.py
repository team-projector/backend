from django.test import override_settings

from apps.development.models import Project
from apps.development.tasks import sync_project_task
from tests.test_development.checkers_gitlab import check_project
from tests.test_development.factories import (
    ProjectFactory,
    ProjectGroupFactory
)
from tests.test_development.factories_gitlab import (
    AttrDict,
    GlGroupFactory,
    GlProjectFactory,
    GlProjectMilestoneFactory,
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_project_task(db, gl_mocker):
    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/milestones',
                           [gl_milestone])

    sync_project_task(group.id, project.id)

    project = Project.objects.get(gl_id=gl_project.id)
    check_project(project, gl_project, group)
