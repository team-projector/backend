# -*- coding: utf-8 -*-

import pytest

from tests.test_development.factories import (
    MilestoneFactory,
    ProjectMilestoneFactory,
    TicketFactory,
)


@pytest.fixture(scope="session")
def sync_milestone_mutation(ghl_mutations):
    """Sync milestone mutation."""
    return ghl_mutations.fields["syncMilestone"].resolver


@pytest.fixture()
def ticket(db):
    """
    Ticket.

    :param db:
    """
    return TicketFactory(milestone=ProjectMilestoneFactory())


@pytest.fixture()
def milestone(user):
    """
    Milestone.

    :param user:
    """
    return MilestoneFactory(user=user)
