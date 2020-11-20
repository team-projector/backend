from unittest.mock import patch

import pytest

from apps.development.services.issue.labels import handle_done_label
from tests.test_development.factories import (
    IssueFactory,
    LabelFactory,
    TicketFactory,
)


@pytest.fixture()
def patched_notify_task():
    """Mocking celery task here."""
    with patch(
        "apps.development.tasks.notify_if_ticket_completed_task.delay",
    ) as mock:
        yield mock


@pytest.fixture(autouse=True)
def _mock_on_issue_labeling():
    """We disable m2m signal here."""
    with patch(
        "apps.development.services.issue.labels.on_issue_labeling",
    ):
        yield


def test_handle_done_label_no_ticket(db, patched_notify_task):
    """Don't send notification if there's no ticket."""
    label = LabelFactory.create(title="Done")
    issue = IssueFactory.create()
    issue.labels.add(label)

    handle_done_label(issue, {label.pk})
    patched_notify_task.assert_not_called()


def test_handle_done_label_no_right_label(db, patched_notify_task):
    """Don't send notification if wrong(not `done`) label added."""
    label = LabelFactory.create(title="Don")
    issue = IssueFactory.create(ticket=TicketFactory.create())
    issue.labels.add(label)

    handle_done_label(issue, {label.pk})
    patched_notify_task.assert_not_called()


def test_handle_done_label_wrong_label_added(db, patched_notify_task):
    """Don't send notification if wrong(not `done`) label added."""
    label = LabelFactory.create(title="Done")
    issue = IssueFactory.create(ticket=TicketFactory.create())
    issue.labels.add(label)

    handle_done_label(issue, {label.pk + 1})
    patched_notify_task.assert_not_called()


def test_handle_done_label_right_label_added(db, patched_notify_task):
    """All requirements are met so notification task should be triggered."""
    label = LabelFactory.create(title="Done")
    ticket = TicketFactory.create()
    issue = IssueFactory.create(ticket=ticket)
    issue.labels.add(label)

    handle_done_label(issue, {label.pk})
    patched_notify_task.assert_called_once_with(ticket.pk)
