import pytest


@pytest.fixture(scope="session")
def all_project_groups_query(ghl_queries):
    """
    All project groups query.

    :param ghl_queries:
    """
    return ghl_queries.fields["allProjectGroups"].resolver


@pytest.fixture(scope="session")
def project_groups_summary_query(ghl_queries):
    """
    Project groups summary query.

    :param ghl_queries:
    """
    return ghl_queries.fields["projectGroupsSummary"].resolver
