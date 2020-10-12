from apps.development.tasks import propagate_ticket_to_related_issues_task
from tests.test_development.factories import IssueFactory


def test_propagate_ticket_issue_exists(db):
    """Test propagate ticket to related issues if issue exists."""
    issue = IssueFactory.create()

    assert propagate_ticket_to_related_issues_task(issue.pk) is None


def test_propagate_ticket_issue_not_exists(db):
    """Test propagate ticket to related issues if issue not exists."""
    issue = IssueFactory.create()

    assert propagate_ticket_to_related_issues_task(issue.pk + 1) is None
