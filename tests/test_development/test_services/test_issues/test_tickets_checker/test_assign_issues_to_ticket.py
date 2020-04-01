# -*- coding: utf-8 -*-

from apps.development.services.issue.tickets_checker import (
    assign_issues_to_ticket,
    get_related_issues,
)
from tests.test_development.factories import IssueFactory, TicketFactory


def test_assign_ticket(db):
    url_template = "https://gitlab.com/junte/team-projector/backend/issues/{0}"
    issue1 = IssueFactory.create(
        ticket=None, gl_url=url_template.format("12"),
    )
    issue2 = IssueFactory.create(
        ticket=TicketFactory.create(), description=issue1.gl_url,
    )

    assign_issues_to_ticket(issue2)
    issue1.refresh_from_db()

    assert issue1.ticket == issue2.ticket


def test_issuewithout_ticket(db):
    url_template = "https://gitlab.com/junte/team-projector/backend/issues/{0}"
    issue1 = IssueFactory.create(
        ticket=None, gl_url=url_template.format("12"),
    )
    issue2 = IssueFactory.create(ticket=None, description=issue1.gl_url)

    assign_issues_to_ticket(issue2)

    assert not issue1.ticket
    assert get_related_issues(issue2).count() == 1
