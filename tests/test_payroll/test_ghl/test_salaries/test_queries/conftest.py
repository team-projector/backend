import pytest


@pytest.fixture(scope="session")
def all_salaries_query(ghl_queries):
    """
    All salaries query.

    :param ghl_queries:
    """
    return ghl_queries.fields["allSalaries"].resolver


@pytest.fixture(scope="session")
def salary_query(ghl_queries):
    """
    Salary query.

    :param ghl_queries:
    """
    return ghl_queries.fields["salary"].resolver
