from apps.development.services.team.metrics.main import TeamMetrics


def check_team_metrics(
    metrics: TeamMetrics,
    problems_count=0,
    issues_count=0,
    issues_opened_count=0,
    issues_opened_estimated=0,
    merge_requests_count=0,
    merge_requests_opened_count=0,
    merge_requests_opened_estimated=0,
):
    assert metrics.problems_count == problems_count

    issues_metrics = metrics.issues
    assert issues_metrics.count == issues_count
    assert issues_metrics.opened_count == issues_opened_count
    assert issues_metrics.opened_estimated == issues_opened_estimated

    mr_metrics = metrics.merge_requests
    assert mr_metrics.count == merge_requests_count
    assert mr_metrics.opened_count == merge_requests_opened_count
    assert mr_metrics.opened_estimated == merge_requests_opened_estimated