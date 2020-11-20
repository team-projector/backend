from unittest.mock import patch

import pytest

from apps.core.notifications import slack
from apps.development.services.ticket.state import TicketCompletionService
from tests.test_development.factories import (
    IssueFactory,
    LabelFactory,
    TicketFactory,
)

_service = TicketCompletionService()


@pytest.fixture()
def mock_send_blocks():
    """Mocking slack client send_message api."""
    with patch(
        "apps.core.notifications.slack.send_blocks",
    ) as mock:
        yield mock


@pytest.fixture(autouse=True)
def _mock_handle_issue_labeling():
    """We disable m2m signal here."""
    with patch(
        "apps.development.services.issue.labels.handle_issue_labeling",
    ):
        yield


def test_notify_if_completed_issue_not_done(
    project_manager,
    project,
    mock_send_blocks,
):
    """Issue doesn't have the `done` label, notification shouldn't be sent."""
    ticket = TicketFactory.create()
    IssueFactory.create(ticket=ticket, project=project)

    _service.notify_if_completed(ticket)
    mock_send_blocks.assert_not_called()


def test_notify_if_completed(project_manager, project, mock_send_blocks):
    """All requirements are met so notification should be sent."""
    ticket = TicketFactory.create()
    issue = IssueFactory.create(ticket=ticket, project=project)
    label = LabelFactory.create(title="done")
    issue.labels.add(label)

    _service.notify_if_completed(ticket)
    mock_send_blocks.assert_called_once_with(
        project_manager,
        slack.render_template_to_blocks(
            "slack/ticket_ready_for_review.json",
            {
                "gitlab_address": "config.GITLAB_ADDRESS",
                "project": project,
                "ticket": ticket,
                "ticket_url": ticket.site_url,
            },
        ),
    )


def test_notify_if_completed_multiple_issues(
    project_manager,
    project,
    mock_send_blocks,
):
    """There should be only the one notification.

    Multiple issues might produce duplicates in the queryset used in this
    method.
    """
    ticket = TicketFactory.create()
    for _ in range(2):  # noqa: WPS122
        issue = IssueFactory.create(ticket=ticket, project=project)
        label = LabelFactory.create(title="done")
        issue.labels.add(label)

    _service.notify_if_completed(ticket)
    mock_send_blocks.assert_called_once_with(
        project_manager,
        slack.render_template_to_blocks(
            "slack/ticket_ready_for_review.json",
            {
                "gitlab_address": "config.GITLAB_ADDRESS",
                "project": project,
                "ticket": ticket,
                "ticket_url": ticket.site_url,
            },
        ),
    )


def test_no_managers(project, mock_send_blocks):
    """No managers - no notifications."""
    ticket = TicketFactory.create()
    issue = IssueFactory.create(ticket=ticket, project=project)
    label = LabelFactory.create(title="done")
    issue.labels.add(label)

    _service.notify_if_completed(ticket)
    mock_send_blocks.assert_not_called()
