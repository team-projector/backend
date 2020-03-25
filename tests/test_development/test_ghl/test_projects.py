# -*- coding: utf-8 -*-

from apps.development.graphql.resolvers import ProjectMilestonesResolver
from apps.development.graphql.types.project import ProjectType
from apps.development.models.milestone import MilestoneState
from tests.helpers.objects import AttrDict
from tests.test_development.factories import (
    ProjectFactory,
    ProjectGroupFactory,
    ProjectGroupMilestoneFactory,
    ProjectMilestoneFactory,
)


def test_project(user, client):
    client.user = user
    info = AttrDict({"context": client})

    project = ProjectFactory.create()

    assert ProjectType().get_node(info, project.id) == project


def test_project_milestones(user, client):
    project = ProjectFactory.create()

    milestone_1 = ProjectMilestoneFactory.create(
        owner=project, state=MilestoneState.ACTIVE,
    )
    milestone_2 = ProjectMilestoneFactory.create(
        owner=project, state=MilestoneState.CLOSED,
    )

    client.user = user
    info = AttrDict({"context": client})

    milestones = ProjectMilestonesResolver(
        project=project, info=info, active=True,
    ).execute()

    assert milestones.count() == 1
    assert milestones.first() == milestone_1

    milestones = ProjectMilestonesResolver(
        project=project, info=info, active=False,
    ).execute()

    assert milestones.count() == 1
    assert milestones.first() == milestone_2


def test_project_group_milestones(user, client):
    group = ProjectGroupFactory.create()

    milestone_1 = ProjectGroupMilestoneFactory.create(
        owner=group, state=MilestoneState.ACTIVE,
    )
    ProjectGroupMilestoneFactory.create_batch(
        3, owner=group, state=MilestoneState.CLOSED,
    )

    project = ProjectFactory.create(group=group)
    milestone_2 = ProjectGroupMilestoneFactory.create(
        owner=project, state=MilestoneState.CLOSED,
    )

    client.user = user
    info = AttrDict({"context": client})

    milestones = ProjectMilestonesResolver(
        project=project, info=info, active=True,
    ).execute()

    assert milestones.count() == 1
    assert milestones.first() == milestone_1

    milestones = ProjectMilestonesResolver(
        project=project, info=info, active=False,
    ).execute()

    assert milestones.count() == 1
    assert milestones.first() == milestone_2


def test_project_group_parent_milestones(user, client):
    group_parent = ProjectGroupFactory.create()

    milestone_1 = ProjectGroupMilestoneFactory.create(
        owner=group_parent, state=MilestoneState.ACTIVE,
    )
    ProjectGroupMilestoneFactory.create_batch(
        3, owner=group_parent, state=MilestoneState.CLOSED,
    )

    group = ProjectGroupFactory.create(parent=group_parent)

    project = ProjectFactory.create(group=group)
    milestone_2 = ProjectGroupMilestoneFactory.create(
        owner=group, state=MilestoneState.CLOSED,
    )

    client.user = user
    info = AttrDict({"context": client})

    milestones = ProjectMilestonesResolver(
        project=project, info=info, active=True,
    ).execute()

    assert milestones.count() == 1
    assert milestones.first() == milestone_1

    milestones = ProjectMilestonesResolver(
        project=project, info=info, active=False,
    ).execute()

    assert milestones.count() == 1
    assert milestones.first() == milestone_2


def test_resolve_milestones(user, client):
    project = ProjectFactory.create()

    ProjectMilestoneFactory.create(owner=project, state=MilestoneState.ACTIVE)
    milestone_2 = ProjectMilestoneFactory.create(
        owner=project, state=MilestoneState.CLOSED,
    )

    client.user = user
    info = AttrDict({"context": client})

    parent = ProjectType.get_node(info, obj_id=project.id)
    parent.parent_type = None

    milestones = ProjectType.resolve_milestones(parent, info, active=False)

    assert milestones.count() == 1
    assert milestones.first() == milestone_2
