from django.test import override_settings
from tests.test_development.checkers_gitlab import check_milestone
from tests.test_development.factories import (
    ProjectFactory,
    ProjectGroupFactory,
)
from tests.test_development.factories_gitlab import (
    AttrDict,
    GlGroupFactory,
    GlProjectMilestoneFactory,
)

from apps.development.models import Milestone
from apps.development.tasks import (
    sync_groups_milestones_task,
    sync_projects_milestones_task,
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_projects_milestones_task(db, gl_mocker):
    gl_project = AttrDict(GlGroupFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}/milestones',
                           [gl_milestone])

    sync_projects_milestones_task()

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)
    check_milestone(milestone, gl_milestone, project)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_groups_milestones_task(db, gl_mocker):
    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    gl_mocker.registry_get(f'/groups/{gl_group.id}/milestones',
                           [gl_milestone])

    sync_groups_milestones_task()

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)
    check_milestone(milestone, gl_milestone, group)
