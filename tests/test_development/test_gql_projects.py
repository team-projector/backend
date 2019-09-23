from apps.development.graphql.resolvers import ProjectMilestonesResolver
from apps.development.graphql.types.project import ProjectType
from apps.development.models.milestone import MILESTONE_STATES
from tests.test_development.factories import (
    ProjectFactory, ProjectGroupFactory, ProjectMilestoneFactory,
    ProjectGroupMilestoneFactory
)
from tests.test_development.factories_gitlab import AttrDict


def test_project(user, client):
    client.user = user
    info = AttrDict({'context': client})

    project = ProjectFactory.create()

    assert ProjectType().get_node(info, project.id) == project


def test_project_milestones(user, client):
    project = ProjectFactory.create()

    milestone_1 = ProjectMilestoneFactory.create(
        owner=project,
        state=MILESTONE_STATES.active
    )
    milestone_2 = ProjectMilestoneFactory.create(
        owner=project,
        state=MILESTONE_STATES.closed
    )

    client.user = user
    info = AttrDict({'context': client})

    milestones = ProjectMilestonesResolver(
        project=project,
        info=info,
        active=True
    ).execute()

    assert milestones.count() == 1
    assert milestones.first() == milestone_1

    milestones = ProjectMilestonesResolver(
        project=project,
        info=info,
        active=False
    ).execute()

    assert milestones.count() == 1
    assert milestones.first() == milestone_2


def test_project_group_milestones(user, client):
    group = ProjectGroupFactory.create()

    milestone_1 = ProjectGroupMilestoneFactory.create(
        owner=group,
        state=MILESTONE_STATES.active
    )
    ProjectGroupMilestoneFactory.create_batch(
        3,
        owner=group,
        state=MILESTONE_STATES.closed
    )

    project = ProjectFactory.create(group=group)
    milestone_2 = ProjectGroupMilestoneFactory.create(
        owner=project,
        state=MILESTONE_STATES.closed
    )

    client.user = user
    info = AttrDict({'context': client})

    milestones = ProjectMilestonesResolver(
        project=project,
        info=info,
        active=True
    ).execute()

    assert milestones.count() == 1
    assert milestones.first() == milestone_1

    milestones = ProjectMilestonesResolver(
        project=project,
        info=info,
        active=False
    ).execute()

    assert milestones.count() == 1
    assert milestones.first() == milestone_2


def test_project_group_parent_milestones(user, client):
    group_parent = ProjectGroupFactory.create()

    milestone_1 = ProjectGroupMilestoneFactory.create(
        owner=group_parent,
        state=MILESTONE_STATES.active
    )
    ProjectGroupMilestoneFactory.create_batch(
        3,
        owner=group_parent,
        state=MILESTONE_STATES.closed
    )

    group = ProjectGroupFactory.create(parent=group_parent)

    project = ProjectFactory.create(group=group)
    milestone_2 = ProjectGroupMilestoneFactory.create(
        owner=group,
        state=MILESTONE_STATES.closed
    )

    client.user = user
    info = AttrDict({'context': client})

    milestones = ProjectMilestonesResolver(
        project=project,
        info=info,
        active=True
    ).execute()

    assert milestones.count() == 1
    assert milestones.first() == milestone_1

    milestones = ProjectMilestonesResolver(
        project=project,
        info=info,
        active=False
    ).execute()

    assert milestones.count() == 1
    assert milestones.first() == milestone_2
