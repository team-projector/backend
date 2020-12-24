import pytest


@pytest.fixture(scope="session")
def user_query(ghl_queries):
    """
    User query.

    :param ghl_queries:
    """
    return ghl_queries.fields["user"].resolver


@pytest.fixture(scope="session")
def all_users_query(ghl_queries):
    """
    All users query.

    :param ghl_queries:
    """
    return ghl_queries.fields["allUsers"].resolver
