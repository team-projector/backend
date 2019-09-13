from apps.development.graphql.types.milestone import MilestoneType
from apps.development.models import Milestone
from tests.test_development.factories import ProjectMilestoneFactory
from tests.test_development.factories_gitlab import AttrDict


def test_milestones(user, client):
    user.roles.project_manager = True
    user.save()

    client.user = user
    info = AttrDict({'context': client})

    ProjectMilestoneFactory.create_batch(5)

    milestones = MilestoneType().get_queryset(
        Milestone.objects.all(), info
    )

    assert milestones.count() == 5


def test_milestone(user, client):
    user.roles.project_manager = True
    user.save()

    client.user = user
    info = AttrDict({'context': client})

    milestone = ProjectMilestoneFactory.create()

    results = MilestoneType().get_node(
        info=info,
        obj_id=milestone.id
    )

    assert results == milestone
