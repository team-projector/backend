from tests.test_development.factories import (
    ProjectFactory,
    ProjectMemberFactory,
    ProjectMilestoneFactory,
)
from tests.test_development.factories_gitlab import AttrDict

from apps.development.graphql.types.milestone import MilestoneType
from apps.development.models import Milestone
from apps.development.models.project_member import PROJECT_MEMBER_ROLES


def test_milestones(user, client):
    project = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=project
    )

    milestone = ProjectMilestoneFactory.create(owner=project)

    client.user = user
    info = AttrDict({'context': client})

    ProjectMilestoneFactory.create_batch(5)

    milestones = MilestoneType().get_queryset(
        Milestone.objects.all(), info
    )

    assert milestones.count() == 1
    assert milestones.first() == milestone


def test_milestone(user, client):
    project = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=PROJECT_MEMBER_ROLES.PROJECT_MANAGER,
        owner=project
    )

    milestone = ProjectMilestoneFactory.create(owner=project)

    client.user = user
    info = AttrDict({'context': client})

    ProjectMilestoneFactory.create_batch(5)

    results = MilestoneType().get_node(
        info, milestone.id
    )

    assert results == milestone
