from apps.development.graphql.types.milestone import MilestoneType
from apps.development.models import Milestone
from apps.development.models.project_member import ProjectMemberRole
from tests.helpers.objects import AttrDict
from tests.test_development.factories import (
    ProjectFactory,
    ProjectMemberFactory,
    ProjectMilestoneFactory,
)


def test_milestones(user, client):
    project = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=ProjectMemberRole.PROJECT_MANAGER,
        owner=project
    )

    milestone = ProjectMilestoneFactory.create(owner=project)

    client.user = user
    info = AttrDict({"context": client})

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
        role=ProjectMemberRole.PROJECT_MANAGER,
        owner=project
    )

    milestone = ProjectMilestoneFactory.create(owner=project)

    client.user = user
    info = AttrDict({"context": client})

    ProjectMilestoneFactory.create_batch(5)

    results = MilestoneType().get_node(
        info, milestone.id
    )

    assert results == milestone
