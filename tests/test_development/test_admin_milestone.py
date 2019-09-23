from django.test import override_settings

from apps.development.models import Milestone
from tests.base import model_admin
from tests.test_development.checkers_gitlab import check_milestone
from tests.test_development.factories import (
    ProjectGroupFactory, ProjectFactory, ProjectMilestoneFactory,
    ProjectGroupMilestoneFactory
)
from tests.test_development.factories_gitlab import (
    AttrDict, GlGroupFactory, GlProjectFactory, GlProjectMilestoneFactory,
    GlUserFactory,
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_group_milestone(db, gl_mocker):
    ma_milestone = model_admin(Milestone)

    gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    milestone = ProjectGroupMilestoneFactory.create(gl_id=gl_milestone.id, owner=group)
    gl_mocker.registry_get(f'/groups/{gl_group.id}/milestones/{gl_milestone.id}',
                           gl_milestone)

    ma_milestone.sync_handler(milestone)

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)

    check_milestone(milestone, gl_milestone, group)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_project_milestone(db, gl_mocker):
    ma_milestone = model_admin(Milestone)

    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_milestone = AttrDict(GlProjectMilestoneFactory())
    milestone = ProjectMilestoneFactory.create(gl_id=gl_milestone.id, owner=project)
    gl_mocker.registry_get(f'/projects/{gl_project.id}/milestones'
                           f'/{gl_milestone.id}', gl_milestone)

    ma_milestone.sync_handler(milestone)

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)

    check_milestone(milestone, gl_milestone, project)
