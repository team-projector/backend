from datetime import date
from unittest.mock import MagicMock

import pytest

from apps.development.services.issue.gl.manager import IssueGlManager
from apps.development.tasks import (
    propagate_ticket_to_related_issues_task,
    sync_project_issues_task,
)
from tests.test_development.factories import IssueFactory, ProjectFactory


@pytest.fixture()
def mocked_sync_project_issues():
    """Mocking IssueGlManager method."""
    mock = MagicMock()
    original = IssueGlManager.sync_project_issues
    IssueGlManager.sync_project_issues = mock
    yield mock
    IssueGlManager.sync_project_issues = original


def test_propagate_ticket_issue_exists(db):
    """Test propagate ticket to related issues if issue exists."""
    issue = IssueFactory.create()

    assert propagate_ticket_to_related_issues_task(issue.pk) is None


def test_propagate_ticket_issue_not_exists(db):
    """Test propagate ticket to related issues if issue not exists."""
    issue = IssueFactory.create()

    assert propagate_ticket_to_related_issues_task(issue.pk + 1) is None


@pytest.mark.parametrize(
    ("gitlab_sync_start_date", "start_date"),
    [
        (None, None),
        ("", None),
        (date(2020, 5, 30), date(2020, 5, 30)),
    ],
)
def test_sync_project_issues_start_date(
    mocked_sync_project_issues,
    db,
    override_config,
    gitlab_sync_start_date,
    start_date,
):
    """Check start_date propagated to manager from constance."""
    project = ProjectFactory.create()
    with override_config(GITLAB_SYNC_START_DATE=gitlab_sync_start_date):
        sync_project_issues_task(project_id=project.pk)
    mocked_sync_project_issues.assert_called_once_with(
        project,
        start_date=start_date,
    )
