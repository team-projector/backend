from apps.development.graphql.types.milestone import MilestoneType
from apps.development.models import Milestone, ProjectMember
from tests.test_development.factories import (
    ProjectFactory, ProjectMilestoneFactory, ProjectMemberFactory
)
from tests.test_development.factories_gitlab import AttrDict


def test_milestones(user, client):
    project = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=user,
        role=ProjectMember.ROLE.project_manager,
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
