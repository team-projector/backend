import pytest


@pytest.fixture(scope='session')
def merge_request_summary_query(ghl_queries):
    return ghl_queries.fields['mergeRequestsSummary'].resolver


@pytest.fixture(scope='session')
def all_merge_requests_query(ghl_queries):
    return ghl_queries.fields['allMergeRequests'].resolver
