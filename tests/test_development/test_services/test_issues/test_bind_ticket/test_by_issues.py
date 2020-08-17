# -*- coding: utf-8 -*-

from apps.development.services.issue.related import get_related_issues
from apps.development.services.issue.tickets.updater import update_issue_ticket
from tests.test_development.factories import IssueFactory, TicketFactory


def test_assign_ticket(db):
    """
    Test assign ticket.

    :param db:
    """
    url_template = "https://gitlab.com/junte/team-projector/backend/issues/{0}"
    issue1 = IssueFactory.create(
        ticket=TicketFactory.create(), gl_url=url_template.format("12"),
    )
    issue2 = IssueFactory.create(ticket=None, description=issue1.gl_url)

    update_issue_ticket(issue2)

    assert issue2.ticket == issue1.ticket


def test_issue_without_ticket(db):
    """
    Test issue without ticket.

    :param db:
    """
    url_template = "https://gitlab.com/junte/team-projector/backend/issues/{0}"
    issue1 = IssueFactory.create(
        ticket=None, gl_url=url_template.format("12"),
    )
    issue2 = IssueFactory.create(ticket=None, description=issue1.gl_url)

    update_issue_ticket(issue2)
    assert get_related_issues(issue2).count() == 1

    assert issue2.ticket is None


def test_already_has_ticket(db):
    """
    Test already has ticket.

    :param db:
    """
    url_template = "https://gitlab.com/junte/team-projector/backend/issues/{0}"
    issue1 = IssueFactory.create(
        ticket=TicketFactory.create(), gl_url=url_template.format("12"),
    )
    issue2 = IssueFactory.create(
        ticket=TicketFactory.create(), description=issue1.gl_url,
    )

    update_issue_ticket(issue2)
    assert issue2.ticket != issue1.ticket
