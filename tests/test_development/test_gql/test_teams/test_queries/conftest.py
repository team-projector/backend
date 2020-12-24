import pytest

SCOPE_SESSION = "session"


@pytest.fixture(scope=SCOPE_SESSION)
def all_teams_query(ghl_queries):
    """
    All teams query.

    :param ghl_queries:
    """
    return ghl_queries.fields["allTeams"].resolver


@pytest.fixture(scope=SCOPE_SESSION)
def team_query(ghl_queries):
    """
    Team query.

    :param ghl_queries:
    """
    return ghl_queries.fields["team"].resolver


@pytest.fixture(scope=SCOPE_SESSION)
def team_progress_metrics_query(ghl_queries):
    """
    Team progress metrics query.

    :param ghl_queries:
    """
    return ghl_queries.fields["teamProgressMetrics"].resolver


@pytest.fixture(scope=SCOPE_SESSION)
def team_work_breaks_query(ghl_queries):
    """
    Team work breaks query.

    :param ghl_queries:
    """
    return ghl_queries.fields["teamWorkBreaks"].resolver
