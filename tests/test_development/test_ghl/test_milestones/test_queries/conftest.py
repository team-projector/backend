# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(scope="session")
def all_milestones_query(ghl_queries):
    return ghl_queries.fields["allMilestones"].resolver
