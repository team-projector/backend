# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(scope="session")
def all_spent_times_query(ghl_queries):
    return ghl_queries.fields["allSpentTimes"].resolver
