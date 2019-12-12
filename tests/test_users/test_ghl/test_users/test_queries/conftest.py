# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(scope='session')
def login_mutation(ghl_mutations):
    return ghl_mutations.fields['login'].resolver


@pytest.fixture(scope='session')
def logout_mutation(ghl_mutations):
    return ghl_mutations.fields['logout'].resolver


@pytest.fixture(scope='session')
def me_query(ghl_queries):
    return ghl_queries.fields['me'].resolver
