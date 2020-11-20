from unittest.mock import patch

import pytest

from tests.test_development.factories import IssueFactory, LabelFactory


@pytest.fixture()
def patched_handle_issue_labeling():
    """Mocking handle_issue_labeling to test m2m signal logic separately."""
    with patch(
        "apps.development.services.issue.labels.handle_issue_labeling",
    ) as mock:
        yield mock


def test_handle_issue_labeling_label_add(db, patched_handle_issue_labeling):
    """A new added label should trigger handle_issue_labeling."""
    issue = IssueFactory.create()
    label = LabelFactory.create()
    issue.labels.add(label)

    patched_handle_issue_labeling.assert_called_once_with(issue, {label.pk})


def test_handle_issue_labeling_label_set(db, patched_handle_issue_labeling):
    """A new added via `set` label should trigger handle_issue_labeling."""
    issue = IssueFactory.create()
    label = LabelFactory.create()
    issue.labels.set([label])

    patched_handle_issue_labeling.assert_called_once_with(issue, {label.pk})


def test_handle_issue_labeling_label_add_twice(
    db,
    patched_handle_issue_labeling,
):
    """Subsequently added labels shouldn't trigger handle_issue_labeling."""
    issue = IssueFactory.create()
    label = LabelFactory.create()
    issue.labels.add(label)
    issue.labels.add(label)

    patched_handle_issue_labeling.assert_called_once_with(issue, {label.pk})


def test_handle_issue_labeling_label_set_twice(
    db,
    patched_handle_issue_labeling,
):
    """Subsequently added labels shouldn't trigger handle_issue_labeling."""
    issue = IssueFactory.create()
    label = LabelFactory.create()
    issue.labels.set([label])
    issue.labels.set([label])

    patched_handle_issue_labeling.assert_called_once_with(issue, {label.pk})
