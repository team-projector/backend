import pytest

from tests.test_development.factories import (
    IssueFactory,
    ProjectMilestoneFactory,
    TicketFactory,
)


@pytest.fixture(scope="session")
def add_spent_issue_mutation(ghl_mutations):
    """Add spent to issue mutation."""
    return ghl_mutations.fields["addSpendTimeIssue"].resolver


@pytest.fixture(scope="session")
def sync_issue_mutation(ghl_mutations):
    """Sync issue mutation."""
    return ghl_mutations.fields["syncIssue"].resolver


@pytest.fixture(scope="session")
def update_issue_mutation(ghl_mutations):
    """Update issue mutation."""
    return ghl_mutations.fields["updateIssue"].resolver


@pytest.fixture()
def ticket(db):
    """
    Ticket.

    :param db:
    """
    return TicketFactory.create(milestone=ProjectMilestoneFactory())


@pytest.fixture()
def issue(user):
    """
    Issue.

    :param user:
    """
    return IssueFactory.create(user=user)
