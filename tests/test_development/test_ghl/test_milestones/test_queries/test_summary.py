# -*- coding: utf-8 -*-

import pytest

from apps.development.models.milestone import MilestoneState
from apps.development.models.project_member import ProjectMemberRole
from tests.test_development.factories import (
    ProjectFactory,
    ProjectMemberFactory,
    ProjectMilestoneFactory,
)

GHL_QUERY_MILESTONES_SUMMARY = """
query {
    milestonesSummary {
        count
        activeCount
        closedCount
    }
}
"""


@pytest.fixture()
def milestones(user):
    project = ProjectFactory.create()
    ProjectMemberFactory.create(
        user=user, role=ProjectMemberRole.PROJECT_MANAGER, owner=project
    )
    return (
        ProjectMilestoneFactory.create(
            state=MilestoneState.ACTIVE, owner=project,
        ),
        ProjectMilestoneFactory.create(
            state=MilestoneState.CLOSED, owner=project,
        ),
    )


def test_raw_query(gql_client_authenticated, milestones):
    response = gql_client_authenticated.execute(GHL_QUERY_MILESTONES_SUMMARY)

    assert "errors" not in response

    dto = response["data"]["milestonesSummary"]
    assert dto == {"count": 2, "activeCount": 1, "closedCount": 1}


def test_filter_by_state(
    milestones_summary_query, ghl_auth_mock_info, milestones,
):
    response = milestones_summary_query(
        parent=None,
        root=None,
        info=ghl_auth_mock_info,
        state=MilestoneState.ACTIVE,
    )

    assert response == {"count": 1, "active_count": 1, "closed_count": 0}
