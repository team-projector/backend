from django.utils import timezone

from apps.development.graphql.types import IssuesProjectSummary, ProjectType
from apps.development.models.milestone import MILESTONE_STATES
from tests.helpers.objects import AttrDict
from tests.test_development.factories import (
    IssueFactory,
    ProjectMilestoneFactory,
)


def test_active_milestones_sort(user, client):
    user.roles.PROJECT_MANAGER = True
    user.save()

    client.user = user
    info = AttrDict({'context': client})

    m1 = ProjectMilestoneFactory(state=MILESTONE_STATES.ACTIVE)
    ProjectMilestoneFactory(
        state=MILESTONE_STATES.ACTIVE,
        owner=m1.owner
    )
    m3 = ProjectMilestoneFactory(
        state=MILESTONE_STATES.ACTIVE,
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


def test_resolve_project(user):
    issue = IssueFactory.create(user=user)

    project = IssuesProjectSummary.resolve_project(issue, None)

    assert project == issue.project
