from tests.test_payroll.factories import PenaltyFactory
from tests.test_users.factories import UserFactory


def test_query(user, gql_client, gql_raw):
    """
    Test query.

    :param user:
    :param gql_client:
    """
    penalty = PenaltyFactory.create(user=user)
    gql_client.set_user(user)

    response = gql_client.execute(
        gql_raw("penalty"),
        variable_values={"id": penalty.pk},
    )

    assert "errors" not in response
    assert response["data"]["penalty"]["id"] == str(penalty.pk)


def test_unauth(db, ghl_mock_info, penalty_query, user):
    """
    Test unauth.

    :param db:
    :param ghl_mock_info:
    :param penalty_query:
    :param user:
    """
    penalty = PenaltyFactory.create(user=user)

    response = penalty_query(
        root=None,
        info=ghl_mock_info,
        id=penalty.pk,
    )

    assert response is None


def test_not_found(ghl_auth_mock_info, penalty_query):
    """
    Test not found.

    :param ghl_auth_mock_info:
    :param penalty_query:
    """
    response = penalty_query(
        root=None,
        info=ghl_auth_mock_info,
        id=1,
    )

    assert response is None


def test_not_allowed_for_user(user, penalty_query, ghl_auth_mock_info):
    """
    Test not allowed for user.

    :param user:
    :param penalty_query:
    :param ghl_auth_mock_info:
    """
    penalty = PenaltyFactory.create(user=UserFactory.create())
    response = penalty_query(
        root=None,
        info=ghl_auth_mock_info,
        id=penalty.pk,
    )

    assert response is None
