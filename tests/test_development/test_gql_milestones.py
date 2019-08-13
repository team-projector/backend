from pytest import raises
from django.core.exceptions import PermissionDenied

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


def test_milestones_not_pm(user, client):
    client.user = user
    info = AttrDict({'context': client})

    ProjectMilestoneFactory.create_batch(5)

    with raises(PermissionDenied):
        MilestoneType().get_queryset(
            Milestone.objects.all(), info
        )
