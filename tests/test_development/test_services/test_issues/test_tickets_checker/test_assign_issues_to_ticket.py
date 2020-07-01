# -*- coding: utf-8 -*-

from apps.development.services.issue.tickets_checker import (
    adjust_issue_ticket,
    get_related_issues,
)
from tests.test_development.factories import IssueFactory, TicketFactory


def test_assign_ticket(db):
    url_template = "https://gitlab.com/junte/team-projector/backend/issues/{0}"
    issue1 = IssueFactory.create(
        ticket=TicketFactory.create(), gl_url=url_template.format("12"),
    )
    issue2 = IssueFactory.create(ticket=None, description=issue1.gl_url)

    adjust_issue_ticket(issue2)

    assert issue2.ticket == issue1.ticket


def test_issue_without_ticket(db):
    url_template = "https://gitlab.com/junte/team-projector/backend/issues/{0}"
    issue1 = IssueFactory.create(
        ticket=None, gl_url=url_template.format("12"),
    )
    issue2 = IssueFactory.create(ticket=None, description=issue1.gl_url)

    adjust_issue_ticket(issue2)
    assert get_related_issues(issue2).count() == 1

    assert issue2.ticket is None


def test_already_has_ticket(db):
    url_template = "https://gitlab.com/junte/team-projector/backend/issues/{0}"
    issue1 = IssueFactory.create(
        ticket=TicketFactory.create(), gl_url=url_template.format("12"),
    )
    issue2 = IssueFactory.create(
        ticket=TicketFactory.create(), description=issue1.gl_url,
    )

    adjust_issue_ticket(issue2)
    assert issue2.ticket != issue1.ticket
