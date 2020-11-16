from apps.development.models.choices.project_state import ProjectState
from tests.test_development.factories import ProjectGroupFactory


def test_raw_query(user, gql_client_authenticated, ghl_raw):
    """Test getting all project groups raw query."""
    _create_project_groups()
    response = gql_client_authenticated.execute(
        ghl_raw("project_groups_summary"),
    )

    assert "errors" not in response
    summary = response["data"]["projectGroupsSummary"]

    assert summary["count"] == 6
    assert summary["archivedCount"] == 3
    assert summary["supportingCount"] == 1
    assert summary["developingCount"] == 2


def test_query(ghl_auth_mock_info, project_groups_summary_query):
    """Test summary."""
    _create_project_groups()
    response = project_groups_summary_query(
        root=None,
        info=ghl_auth_mock_info,
    )

    assert response.count == 6
    assert response.archived_count == 3
    assert response.supporting_count == 1
    assert response.developing_count == 2


def _create_project_groups() -> None:
    """Create project groups."""
    ProjectGroupFactory.create_batch(3, state=ProjectState.ARCHIVED)
    ProjectGroupFactory.create_batch(2, state=ProjectState.DEVELOPING)
    ProjectGroupFactory.create_batch(1, state=ProjectState.SUPPORTING)
