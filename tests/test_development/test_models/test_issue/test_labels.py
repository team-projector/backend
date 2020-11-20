from unittest.mock import patch

import pytest

from tests.test_development.factories import IssueFactory, LabelFactory


@pytest.fixture()
def patched_on_issue_labeling():
    """Mocking on_issue_labeling to test m2m signal logic separately."""
    with patch(
        "apps.development.services.issue.labels.on_issue_labeling",
    ) as mock:
        yield mock


def test_on_issue_labeling_label_add(db, patched_on_issue_labeling):
    """A new added label should trigger on_issue_labeling."""
    issue = IssueFactory.create()
    label = LabelFactory.create()
    issue.labels.add(label)

    patched_on_issue_labeling.assert_called_once_with(issue, {label.pk})


def test_on_issue_labeling_label_set(db, patched_on_issue_labeling):
    """A new added via `set` label should trigger on_issue_labeling."""
    issue = IssueFactory.create()
    label = LabelFactory.create()
    issue.labels.set([label])

    patched_on_issue_labeling.assert_called_once_with(issue, {label.pk})


def test_on_issue_labeling_label_add_twice(db, patched_on_issue_labeling):
    """Subsequently added labels shouldn't trigger on_issue_labeling."""
    issue = IssueFactory.create()
    label = LabelFactory.create()
    issue.labels.add(label)
    issue.labels.add(label)

    patched_on_issue_labeling.assert_called_once_with(issue, {label.pk})


def test_on_issue_labeling_label_set_twice(db, patched_on_issue_labeling):
    """Subsequently added labels shouldn't trigger on_issue_labeling."""
    issue = IssueFactory.create()
    label = LabelFactory.create()
    issue.labels.set([label])
    issue.labels.set([label])

    patched_on_issue_labeling.assert_called_once_with(issue, {label.pk})
