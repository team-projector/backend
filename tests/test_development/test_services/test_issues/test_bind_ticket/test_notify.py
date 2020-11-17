import pytest
from httpretty import UnmockedError

from apps.development.models.project_member import ProjectMemberRole
from apps.development.services.issue.tickets.updater import update_issue_ticket
from tests.helpers.db import trigger_on_commit
from tests.test_development.factories import (
    IssueFactory,
    ProjectFactory,
    ProjectMemberFactory,
    TicketFactory,
)


def test_assign_ticket(db, slack):
    """Test assign ticket."""
    url_template = "https://gitlab.com/junte/team-projector/backend/issues/{0}"

    project = ProjectFactory.create()
    issue1 = IssueFactory.create(
        project=project,
        ticket=TicketFactory.create(),
        gl_url=url_template.format("12"),
    )
    issue2 = IssueFactory.create(
        project=project,
        ticket=None,
        description=issue1.gl_url,
    )

    ProjectMemberFactory.create(
        owner=project,
        role=ProjectMemberRole.MANAGER,
    )

    update_issue_ticket(issue2)
    assert issue2.ticket == issue1.ticket

    with pytest.raises(UnmockedError):
        trigger_on_commit()
