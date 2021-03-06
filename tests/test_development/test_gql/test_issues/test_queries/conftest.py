import pytest


@pytest.fixture(scope="session")
def issue_query(ghl_queries):
    """
    Issue query.

    :param ghl_queries:
    """
    return ghl_queries.fields["issue"].resolver


@pytest.fixture(scope="session")
def all_issues_query(ghl_queries):
    """
    All issues query.

    :param ghl_queries:
    """
    return ghl_queries.fields["allIssues"].resolver


@pytest.fixture(scope="session")
def issues_summary_query(ghl_queries):
    """
    Issues summary query.

    :param ghl_queries:
    """
    return ghl_queries.fields["issuesSummary"].resolver
