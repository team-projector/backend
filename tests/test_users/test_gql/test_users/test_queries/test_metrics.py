from datetime import datetime

from apps.users.services.user.metrics.progress.main import GroupProgressMetrics


def test_success_query(user, gql_client, gql_raw):
    """Test user progress metrics raw query."""
    gql_client.set_user(user)

    date = datetime.now().date()

    response = gql_client.execute(
        gql_raw("user_progress_metrics"),
        variable_values={
            "id": user.pk,
            "start": date,
            "end": date,
            "group": GroupProgressMetrics.WEEK.name,
        },
    )

    assert "errors" not in response

    progress_metrics = response["data"]["userProgressMetrics"]

    assert len(progress_metrics) == 1

    metrics = progress_metrics[0]

    assert metrics["start"] == date.strftime("%Y-%m-%d")  # noqa: WPS323
    assert metrics["end"] == date.strftime("%Y-%m-%d")  # noqa: WPS323
    assert not metrics["issuesCount"]
