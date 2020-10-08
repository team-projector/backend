import pytest


@pytest.fixture(scope="session")
def all_work_breaks_query(ghl_queries):
    """Update work break mutation."""
    return ghl_queries.fields["allWorkBreaks"].resolver


@pytest.fixture(scope="session")
def work_break_query(ghl_queries):
    """Update work break mutation."""
    return ghl_queries.fields["workBreak"].resolver
