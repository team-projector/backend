# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(scope="session")
def merge_request_summary_query(ghl_queries):
    """
    Merge request summary query.

    :param ghl_queries:
    """
    return ghl_queries.fields["mergeRequestsSummary"].resolver


@pytest.fixture(scope="session")
def all_merge_requests_query(ghl_queries):
    """
    All merge requests query.

    :param ghl_queries:
    """
    return ghl_queries.fields["allMergeRequests"].resolver
