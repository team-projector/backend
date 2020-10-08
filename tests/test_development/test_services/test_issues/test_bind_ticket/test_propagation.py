from apps.development.services.issue.tickets.propagator import (
    propagate_ticket_to_related_issues,
)
from tests.test_development.factories import IssueFactory, TicketFactory


def test_assign_ticket(db):
    """
    Test assign ticket.

    :param db:
    """
    child_issue = IssueFactory.create(
        ticket=None,
        gl_url="https://gitlab.com/junte/team-projector/backend/issues/12",
    )
    issue = IssueFactory.create(
        ticket=TicketFactory.create(),
        description=child_issue.gl_url,
    )

    propagate_ticket_to_related_issues(issue)
    child_issue.refresh_from_db()

    assert issue.ticket == child_issue.ticket
