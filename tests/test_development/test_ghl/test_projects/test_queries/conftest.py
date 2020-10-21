import pytest


@pytest.fixture(scope="session")
def all_projects_query(ghl_queries):
    """
    All projects query.

    :param ghl_queries:
    """
    return ghl_queries.fields["allProjects"].resolver
