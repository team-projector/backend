from django.test import override_settings

from apps.development.graphql.mutations.milestones import SyncMilestoneMutation
from apps.development.models.milestone import MILESTONE_STATES
from tests.helpers.objects import AttrDict
from tests.test_development.factories import (
    ProjectFactory,
    ProjectGroupFactory,
    ProjectGroupMilestoneFactory,
    ProjectMilestoneFactory,
)
from tests.test_development.factories.gitlab import (
    GlGroupFactory,
    GlGroupMilestoneFactory,
    GlProjectFactory,
    GlProjectMilestoneFactory,
)
from tests.test_users.factories.gitlab import GlUserFactory


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_milestone_group(user, client, gl_mocker):
    gl_group = AttrDict(GlGroupFactory())
    group = ProjectGroupFactory.create(gl_id=gl_group.id)

    gl_milestone = AttrDict(
        GlGroupMilestoneFactory(state=MILESTONE_STATES.CLOSED))
    milestone = ProjectGroupMilestoneFactory.create(
        gl_id=gl_milestone.id, owner=group, state=MILESTONE_STATES.ACTIVE
    )

    gl_mocker.register_get('/user', GlUserFactory())
    gl_mocker.register_get(f'/groups/{gl_group.id}', gl_group)
    gl_mocker.register_get(
        f'/groups/{gl_group.id}/milestones/{gl_milestone.id}', gl_milestone
    )

    assert milestone.state == MILESTONE_STATES.ACTIVE

    client.user = user
    info = AttrDict({
        'context': client
    })

    milestone_mutated = SyncMilestoneMutation().do_mutate(
        None, info, id=milestone.id
    ).milestone

    assert milestone_mutated.id == milestone_mutated.id
    assert milestone_mutated.gl_id == milestone_mutated.gl_id

    milestone.refresh_from_db()
    assert milestone.state == MILESTONE_STATES.CLOSED


@override_settings(GITLAB_TOKEN='GITLAB_TOKEN')
def test_sync_milestone_project(user, client, gl_mocker):
    gl_project = AttrDict(GlProjectFactory())
    project = ProjectFactory.create(gl_id=gl_project.id)

    gl_milestone = AttrDict(
        GlProjectMilestoneFactory(state=MILESTONE_STATES.CLOSED))
    milestone = ProjectMilestoneFactory.create(
        gl_id=gl_milestone.id, owner=project, state=MILESTONE_STATES.ACTIVE
    )

    gl_mocker.register_get('/user', GlUserFactory())
    gl_mocker.register_get(f'/projects/{gl_project.id}', gl_project)
    gl_mocker.register_get(
        f'/projects/{gl_project.id}/milestones/{gl_milestone.id}', gl_milestone
    )

    assert milestone.state == MILESTONE_STATES.ACTIVE

    client.user = user
    info = AttrDict({
        'context': client
    })

    milestone_mutated = SyncMilestoneMutation().do_mutate(
        None, info, id=milestone.id
    ).milestone

    assert milestone_mutated.id == milestone_mutated.id
    assert milestone_mutated.gl_id == milestone_mutated.gl_id

    milestone.refresh_from_db()
    assert milestone.state == MILESTONE_STATES.CLOSED


def test_sync_milestone_inccorect_owner(user, client):
    milestone = ProjectMilestoneFactory.create(
        owner=user, state=MILESTONE_STATES.ACTIVE
    )

    client.user = user
    info = AttrDict({
        'context': client
    })

    SyncMilestoneMutation().do_mutate(
        None, info, id=milestone.id
    )

    milestone.refresh_from_db()
    assert milestone.state == MILESTONE_STATES.ACTIVE
