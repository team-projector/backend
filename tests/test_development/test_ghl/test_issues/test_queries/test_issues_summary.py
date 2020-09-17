# -*- coding: utf-8 -*-

from apps.development.models.project_member import ProjectMemberRole
from tests.test_development.factories import (
    IssueFactory,
    ProjectFactory,
    ProjectMemberFactory,
    ProjectMilestoneFactory,
)


def test_issues_summary_query(user, gql_client_authenticated, assets):
    """Test getting issues summary raw query."""
    project = ProjectFactory.create()
    milestone = ProjectMilestoneFactory.create(owner=project)
    ProjectMemberFactory.create(
        user=user,
        role=ProjectMemberRole.MANAGER,
        owner=project,
    )
    IssueFactory.create_batch(
        5,
        user=user,
        project=project,
        milestone=milestone,
    )

    query = assets.open_file("issues_summary.ghl", "r").read()

    response = gql_client_authenticated.execute(
        query,
        variable_values={"id": user.pk},
    )

    assert "errors" not in response
    assert response["data"]["issues"]["count"] == 5
