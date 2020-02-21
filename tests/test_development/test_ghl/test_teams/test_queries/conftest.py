# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(scope="session")
def all_teams_query(ghl_queries):
    return ghl_queries.fields["allTeams"].resolver


@pytest.fixture(scope="session")
def team_query(ghl_queries):
    return ghl_queries.fields["team"].resolver


@pytest.fixture(scope="session")
def team_progress_metrics_query(ghl_queries):
    return ghl_queries.fields["teamProgressMetrics"].resolver
