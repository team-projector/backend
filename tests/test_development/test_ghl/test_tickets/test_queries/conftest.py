# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(scope='session')
def ticket_query(ghl_queries):
    return ghl_queries.fields['ticket'].resolver


@pytest.fixture(scope='session')
def all_tickets_query(ghl_queries):
    return ghl_queries.fields['allTickets'].resolver
