from django.utils import timezone

from apps.development.graphql.types import ProjectType
from apps.development.models import Milestone
from apps.development.services.summary.issues import IssuesProjectSummary
from tests.test_development.factories import ProjectMilestoneFactory
from tests.test_development.factories_gitlab import AttrDict


def test_active_milestones_sort(user, client):
    user.roles.project_manager = True
    user.save()

    client.user = user
    info = AttrDict({'context': client})

    m1 = ProjectMilestoneFactory(state=Milestone.STATE.active)
    ProjectMilestoneFactory(
        state=Milestone.STATE.active,
        owner=m1.owner
    )
    m3 = ProjectMilestoneFactory(
        state=Milestone.STATE.active,
        owner=m1.owner,
        due_date=timezone.now()
    )

    parent = ProjectType.get_node(info, obj_id=m1.owner.id)
    parent.parent_type = IssuesProjectSummary()

    milestones = ProjectType.resolve_milestones(
        parent,
        info,
        order_by='due_date'
    )

    assert len(milestones) == 3
    assert milestones[0].id == m3.id


def test_active_milestones_sort_desc(user, client):
    user.roles.project_manager = True
    user.save()

    client.user = user
    info = AttrDict({'context': client})

    m1 = ProjectMilestoneFactory(state=Milestone.STATE.active)
    m2 = ProjectMilestoneFactory(
        state=Milestone.STATE.active,
        owner=m1.owner,
        due_date=timezone.now() + timezone.timedelta(days=2)
    )
    ProjectMilestoneFactory(
        state=Milestone.STATE.active,
        owner=m1.owner,
        due_date=timezone.now()
    )

    parent = ProjectType.get_node(info, obj_id=m1.owner.id)
    parent.parent_type = IssuesProjectSummary()

    milestones = ProjectType.resolve_milestones(
        parent,
        info,
        order_by='-due_date'
    )

    assert len(milestones) == 3
    assert milestones[0].id == m2.id
