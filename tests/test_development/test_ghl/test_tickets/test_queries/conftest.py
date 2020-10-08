import pytest


@pytest.fixture(scope="session")
def ticket_query(ghl_queries):
    """
    Ticket query.

    :param ghl_queries:
    """
    return ghl_queries.fields["ticket"].resolver


@pytest.fixture(scope="session")
def all_tickets_query(ghl_queries):
    """
    All tickets query.

    :param ghl_queries:
    """
    return ghl_queries.fields["allTickets"].resolver


@pytest.fixture(scope="session")
def tickets_summary_query(ghl_queries):
    """
    Tickets summary query.

    :param ghl_queries:
    """
    return ghl_queries.fields["ticketsSummary"].resolver
