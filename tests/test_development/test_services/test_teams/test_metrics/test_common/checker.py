from apps.development.services.team.metrics.main import TeamMetrics
from tests.helpers.checkers import assert_instance_fields


def check_team_metrics(  # noqa: WPS211
    metrics: TeamMetrics,
    problems_count=0,
    issues_count=0,
    issues_opened_count=0,
    issues_opened_estimated=0,
    merge_requests_count=0,
    merge_requests_opened_count=0,
    merge_requests_opened_estimated=0,
):
    """
    Check team metrics.

    :param metrics:
    :type metrics: TeamMetrics
    :param problems_count:
    :param issues_count:
    :param issues_opened_count:
    :param issues_opened_estimated:
    :param merge_requests_count:
    :param merge_requests_opened_count:
    :param merge_requests_opened_estimated:
    """
    assert metrics.problems_count == problems_count

    issues_metrics = metrics.issues

    assert_instance_fields(
        issues_metrics,
        count=issues_count,
        opened_count=issues_opened_count,
        opened_estimated=issues_opened_estimated,
    )

    mr_metrics = metrics.merge_requests

    assert_instance_fields(
        mr_metrics,
        count=merge_requests_count,
        opened_count=merge_requests_opened_count,
        opened_estimated=merge_requests_opened_estimated,
    )
