# -*- coding: utf-8 -*-

from django.utils import timezone

from apps.development.graphql.types import IssuesProjectSummary, ProjectType
from apps.development.models.milestone import MilestoneState
from tests.test_development.factories import (
    IssueFactory,
    ProjectMilestoneFactory,
)


def test_active_milestones_sort(user, client, ghl_auth_mock_info):
    """
    Test active milestones sort.

    :param user:
    :param client:
    :param ghl_auth_mock_info:
    """
    user.roles.MANAGER = True
    user.save()

    client.user = user

    m1 = ProjectMilestoneFactory(state=MilestoneState.ACTIVE)
    ProjectMilestoneFactory(state=MilestoneState.ACTIVE, owner=m1.owner)
    m3 = ProjectMilestoneFactory(
        state=MilestoneState.ACTIVE, owner=m1.owner, due_date=timezone.now(),
    )

    parent = ProjectType.get_node(ghl_auth_mock_info, obj_id=m1.owner.id)
    parent.parent_type = IssuesProjectSummary()

    milestones = ProjectType.resolve_milestones(
        parent, ghl_auth_mock_info, order_by="due_date",
    )

    assert len(milestones) == 3
    assert milestones[0].id == m3.id


def test_resolve_project(user):
    """
    Test resolve project.

    :param user:
    """
    issue = IssueFactory.create(user=user)

    project = IssuesProjectSummary.resolve_project(issue, None)

    assert project == issue.project
