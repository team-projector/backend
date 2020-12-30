from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories import UserFactory


def test_query(user, gql_client, gql_raw):
    """
    Test query.

    :param user:
    :param gql_client:
    """
    salary = SalaryFactory.create(user=user)
    gql_client.set_user(user)

    response = gql_client.execute(
        gql_raw("salary"),
        variable_values={"id": salary.pk},
    )

    assert "errors" not in response
    assert response["data"]["salary"]["id"] == str(salary.pk)


def test_unauth(ghl_mock_info, salary_query, user):
    """
    Test unauth.

    :param ghl_mock_info:
    :param salary_query:
    :param user:
    """
    salary = SalaryFactory.create(user=user)

    response = salary_query(
        root=None,
        info=ghl_mock_info,
        id=salary.pk,
    )
    assert response is None


def test_not_found(ghl_auth_mock_info, salary_query):
    """
    Test not found.

    :param ghl_auth_mock_info:
    :param salary_query:
    """
    response = salary_query(
        root=None,
        info=ghl_auth_mock_info,
        id=1,
    )
    assert response is None


def test_not_allowed_for_user(user, salary_query, ghl_auth_mock_info):
    """
    Test not allowed for user.

    :param user:
    :param salary_query:
    :param ghl_auth_mock_info:
    """
    salary = SalaryFactory.create(user=UserFactory.create())
    response = salary_query(
        root=None,
        info=ghl_auth_mock_info,
        id=salary.pk,
    )
    assert response is None
