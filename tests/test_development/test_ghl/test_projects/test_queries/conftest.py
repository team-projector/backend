import pytest


@pytest.fixture(scope="session")
def all_projects_query(ghl_queries):
    """
    All projects query.

    :param ghl_queries:
    """
    return ghl_queries.fields["allProjects"].resolver


@pytest.fixture(scope="session")
def projects_summary_query(ghl_queries):
    """
    Projects summary query.

    :param ghl_queries:
    """
    return ghl_queries.fields["projectsSummary"].resolver
