import pytest


@pytest.fixture(scope="session")
def me_query(ghl_queries):
    """
    Me query.

    :param ghl_queries:
    """
    return ghl_queries.fields["me"].resolver
