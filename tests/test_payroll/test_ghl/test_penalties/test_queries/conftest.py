# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(scope="session")
def all_penalties_query(ghl_queries):
    return ghl_queries.fields["allPenalties"].resolver


@pytest.fixture(scope="session")
def penalty_query(ghl_queries):
    return ghl_queries.fields["penalty"].resolver
