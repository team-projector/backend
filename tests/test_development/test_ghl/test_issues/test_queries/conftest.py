# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(scope='session')
def issue_query(ghl_queries):
    return ghl_queries.fields['issue'].resolver


@pytest.fixture(scope='session')
def all_issues_query(ghl_queries):
    return ghl_queries.fields['allIssues'].resolver
