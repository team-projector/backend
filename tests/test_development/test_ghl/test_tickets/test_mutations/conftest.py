# -*- coding: utf-8 -*-

import pytest

from tests.test_development.factories import (
    ProjectMilestoneFactory,
    TicketFactory,
)


@pytest.fixture(scope="session")
def create_ticket_mutation(ghl_mutations):
    """Create ticket mutation."""
    return ghl_mutations.fields["createTicket"].resolver


@pytest.fixture(scope="session")
def update_ticket_mutation(ghl_mutations):
    """Update ticket mutation."""
    return ghl_mutations.fields["updateTicket"].resolver


@pytest.fixture(scope="session")
def delete_ticket_mutation(ghl_mutations):
    """Delete ticket mutation."""
    return ghl_mutations.fields["deleteTicket"].resolver


@pytest.fixture()
def ticket():
    return TicketFactory(milestone=ProjectMilestoneFactory())


@pytest.fixture()
def project_manager(user):
    """Provide project manager."""
    user.roles.PROJECT_MANAGER = True
    user.save()

    return user
