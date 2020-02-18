# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(scope="session")
def all_salaries_query(ghl_queries):
    return ghl_queries.fields["allSalaries"].resolver


@pytest.fixture(scope="session")
def salary_query(ghl_queries):
    return ghl_queries.fields["salary"].resolver
