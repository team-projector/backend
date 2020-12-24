from apps.development.models.project import ProjectState
from tests.test_development.factories import ProjectFactory


def test_raw_query(user, gql_client_authenticated, gql_raw):
    """Test getting all projects raw query."""
    _create_projects()
    response = gql_client_authenticated.execute(gql_raw("projects_summary"))

    assert "errors" not in response
    summary = response["data"]["projectsSummary"]

    assert summary["count"] == 6
    assert summary["archivedCount"] == 3
    assert summary["supportingCount"] == 1
    assert summary["developingCount"] == 2


def test_query(ghl_auth_mock_info, projects_summary_query):
    """Test summary."""
    _create_projects()
    response = projects_summary_query(
        root=None,
        info=ghl_auth_mock_info,
    )

    assert response.count == 6
    assert response.archived_count == 3
    assert response.supporting_count == 1
    assert response.developing_count == 2


def _create_projects():
    """Create projects."""
    ProjectFactory.create_batch(3, state=ProjectState.ARCHIVED)
    ProjectFactory.create_batch(2, state=ProjectState.DEVELOPING)
    ProjectFactory.create_batch(1, state=ProjectState.SUPPORTING)
