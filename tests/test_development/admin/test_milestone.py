from django.test import override_settings

from apps.development.models import Milestone
from tests.helpers.base import model_admin
from tests.test_development.checkers_gitlab import check_milestone
from tests.test_development.factories import (
    ProjectFactory,
    ProjectGroupFactory,
    ProjectGroupMilestoneFactory,
    ProjectMilestoneFactory,
)
from tests.test_development.factories_gitlab import (
    AttrDict,
    GlGroupFactory,
    GlProjectFactory,
    GlProjectMilestoneFactory,
    GlUserFactory,
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_group_milestone(db, gl_mocker):
    ma_milestone = model_admin(Milestone)

    gl_mocker.registry_get('/user', GlUserFactory())

    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)

    gl_milestone = AttrDict(GlProjectMilestoneFactory(description='sync'))
    milestone = ProjectGroupMilestoneFactory.create(
        gl_id=gl_milestone.id,
        owner=group,
        description='not sync',
    )
    gl_mocker.registry_get(
        f'/groups/{gl_group.id}/milestones/{gl_milestone.id}',
        gl_milestone,
    )

    assert milestone.description == 'not sync'

    ma_milestone.sync_handler(milestone)

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)

    check_milestone(milestone, gl_milestone, group)
    assert milestone.description == 'sync'


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_project_milestone(db, gl_mocker):
    ma_milestone = model_admin(Milestone)

    gl_mocker.registry_get('/user', GlUserFactory())

    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)

    gl_milestone = AttrDict(GlProjectMilestoneFactory(description='sync'))
    milestone = ProjectMilestoneFactory.create(
        gl_id=gl_milestone.id,
        owner=project,
        description='not sync',
    )
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/milestones/{gl_milestone.id}',
        gl_milestone,
    )

    assert milestone.description == 'not sync'

    ma_milestone.sync_handler(milestone)

    milestone = Milestone.objects.get(gl_id=gl_milestone.id)

    check_milestone(milestone, gl_milestone, project)
    assert milestone.description == 'sync'


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_not_syncing(user):
    ma_milestone = model_admin(Milestone)

    milestone = ProjectMilestoneFactory.create(owner=user,
                                               description='not sync')

    ma_milestone.sync_handler(milestone)

    assert milestone.description == 'not sync'

    milestone = Milestone.objects.first()

    assert milestone.description == 'not sync'
