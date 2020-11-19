import pytest

from apps.development.models.note import NoteType
from apps.development.services.issue.tickets.updater import update_issue_ticket
from tests.test_development.factories import (
    IssueFactory,
    IssueNoteFactory,
    TicketFactory,
)


@pytest.mark.parametrize(
    "description",
    [
        (
            "https://teamprojector.com/en/manager/milestones/1;ticket={0}"
            + " https://teamprojector.com/en/manager/milestones/1;ticket=150 "
        ),
        (
            "ticket https://teamprojector.com/tickets/{0} ticket "
            + "https://teamprojector.com/en/manager/milestones/1;ticket={0}"
        ),
        "\n\n\n\n\n ticket https://teamprojector.com/tickets/{0}",
        (
            "ticket https://teamprojector.com/tickets/{0}"
            + "https://teamprojector.com/tickets/{0}"
        ),
    ],
)
def test_by_description(db, description):
    """
    Test by description.

    :param db:
    """
    ticket = TicketFactory.create()
    issue = IssueFactory.create(description=description.format(ticket.pk))

    update_issue_ticket(issue)

    assert issue.ticket == ticket


def test_by_notes(db):
    """
    Test by notes.

    :param db:
    """
    ticket = TicketFactory.create()
    issue = IssueFactory.create(description="")

    IssueNoteFactory.create(
        data={"tickets": [str(ticket.pk)]},
        content_object=issue,
        type=NoteType.COMMENT,
    )

    update_issue_ticket(issue)

    assert issue.ticket == ticket


def test_ticket_not_exists(db):
    """
    Test ticket not exists.

    :param db:
    """
    ticket = TicketFactory.create()
    issue = IssueFactory.create(description="")

    IssueNoteFactory.create(
        data={"tickets": [str(ticket.pk + 10)]},
        content_object=issue,
        type=NoteType.COMMENT,
    )

    update_issue_ticket(issue)

    assert issue.ticket is None
