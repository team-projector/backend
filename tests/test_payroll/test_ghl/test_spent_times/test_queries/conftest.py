import pytest


@pytest.fixture(scope="session")
def all_spent_times_query(ghl_queries):
    """
    All spent times query.

    :param ghl_queries:
    """
    return ghl_queries.fields["allSpentTimes"].resolver
