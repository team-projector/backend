# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(scope='session')
def me_query(ghl_queries):
    return ghl_queries.fields['me'].resolver
