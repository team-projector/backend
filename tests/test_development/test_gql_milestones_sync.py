from django.test import override_settings

from apps.development.graphql.mutations.milestones import SyncMilestoneMutation
from tests.test_development.factories import (
    ProjectGroupFactory, ProjectGroupMilestoneFactory, ProjectFactory,
    ProjectMilestoneFactory
)
from tests.test_development.factories_gitlab import (
    AttrDict, GlUserFactory, GlGroupFactory, GlGroupMilestoneFactory,
    GlProjectFactory, GlProjectMilestoneFactory
)


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_group(user, client, gl_mocker):
    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)

    gl_milestone = AttrDict(GlGroupMilestoneFactory(state='closed'))
    milestone = ProjectGroupMilestoneFactory.create(
        gl_id=gl_milestone.id, owner=group, state='active'
    )

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/groups/{gl_group.id}', gl_group)
    gl_mocker.registry_get(
        f'/groups/{gl_group.id}/milestones/{gl_milestone.id}', gl_milestone
    )

    assert milestone.state == 'active'

    client.user = user
    info = AttrDict({
        'context': client
    })

    milestone_mutated = SyncMilestoneMutation().do_mutate(
        None, info, milestone.id
    ).milestone

    assert milestone_mutated.id == milestone_mutated.id
    assert milestone_mutated.gl_id == milestone_mutated.gl_id

    milestone.refresh_from_db()
    assert milestone.state == 'closed'


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_project(user, client, gl_mocker):
    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)

    gl_milestone = AttrDict(GlProjectMilestoneFactory(state='closed'))
    milestone = ProjectMilestoneFactory.create(
        gl_id=gl_milestone.id, owner=project, state='active'
    )

    gl_mocker.registry_get('/user', GlUserFactory())
    gl_mocker.registry_get(f'/projects/{gl_project.id}', gl_project)
    gl_mocker.registry_get(
        f'/projects/{gl_project.id}/milestones/{gl_milestone.id}', gl_milestone
    )

    assert milestone.state == 'active'

    client.user = user
    info = AttrDict({
        'context': client
    })

    milestone_mutated = SyncMilestoneMutation().do_mutate(
        None, info, milestone.id
    ).milestone

    assert milestone_mutated.id == milestone_mutated.id
    assert milestone_mutated.gl_id == milestone_mutated.gl_id

    milestone.refresh_from_db()
    assert milestone.state == 'closed'
