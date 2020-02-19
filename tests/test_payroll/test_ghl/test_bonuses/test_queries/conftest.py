# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(scope="session")
def all_bonuses_query(ghl_queries):
    return ghl_queries.fields["allBonuses"].resolver


@pytest.fixture(scope="session")
def bonus_query(ghl_queries):
    return ghl_queries.fields["bonus"].resolver
