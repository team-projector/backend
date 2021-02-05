from datetime import datetime

from tests.test_users.factories import UserFactory


def test_raw_query(manager, gql_client_authenticated, gql_raw):
    """Test success raw query."""
    UserFactory.create(roles=0)
    response = gql_client_authenticated.execute(
        gql_raw("work_calendar"),
        variable_values={
            "user": manager.pk,
            "start": datetime.now().date(),
            "end": datetime.now().date(),
        },
    )

    assert "errors" not in response
    assert len(response["data"]["days"]) == 1

    calendar = response["data"]["days"][0]
    assert calendar["date"] == datetime.now().strftime(
        "%Y-%m-%d",  # noqa: WPS323
    )
    assert calendar["metrics"]
    assert not calendar["issues"]
