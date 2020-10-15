from datetime import date
from unittest.mock import MagicMock

import pytest

from apps.development.services.merge_request.gl.manager import (
    MergeRequestGlManager,
)
from apps.development.tasks import sync_project_merge_requests_task
from tests.test_development.factories import ProjectFactory


@pytest.fixture()
def mocked_sync_project_merge_requests():
    """Mocking MergeRequestGlManager method."""
    mock = MagicMock()
    original = MergeRequestGlManager.sync_merge_requests
    MergeRequestGlManager.sync_project_merge_requests = mock

    yield mock

    MergeRequestGlManager.sync_merge_requests = original


@pytest.mark.parametrize(
    ("gitlab_sync_start_date", "start_date"),
    [
        (None, None),
        ("", None),
        (date(2020, 5, 30), date(2020, 5, 30)),
    ],
)
def test_sync_project_issues_start_date(
    mocked_sync_project_merge_requests,
    db,
    override_config,
    gitlab_sync_start_date,
    start_date,
):
    """Check start_date propagated to manager from constance."""
    project = ProjectFactory.create()
    with override_config(GITLAB_SYNC_START_DATE=gitlab_sync_start_date):
        sync_project_merge_requests_task(project_id=project.pk)
    mocked_sync_project_merge_requests.assert_called_once_with(
        project,
        start_date=start_date,
    )
