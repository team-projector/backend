import pytest
from jnt_django_graphene_toolbox.errors import (
    GraphQLNotFound,
    GraphQLPermissionDenied,
)

from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories import UserFactory


def test_query(user, gql_client, ghl_raw):
    """
    Test query.

    :param user:
    :param gql_client:
    """
    salary = SalaryFactory(user=user)
    gql_client.set_user(user)

    response = gql_client.execute(
        ghl_raw("salary"),
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
    salary = SalaryFactory(user=user)

    with pytest.raises(GraphQLPermissionDenied):
        salary_query(
            root=None,
            info=ghl_mock_info,
            id=salary.pk,
        )


def test_not_found(ghl_auth_mock_info, salary_query):
    """
    Test not found.

    :param ghl_auth_mock_info:
    :param salary_query:
    """
    with pytest.raises(GraphQLNotFound):
        salary_query(
            root=None,
            info=ghl_auth_mock_info,
            id=1,
        )


def test_not_allowed_for_user(user, salary_query, ghl_auth_mock_info):
    """
    Test not allowed for user.

    :param user:
    :param salary_query:
    :param ghl_auth_mock_info:
    """
    salary = SalaryFactory(user=UserFactory())
    with pytest.raises(GraphQLNotFound):
        salary_query(
            root=None,
            info=ghl_auth_mock_info,
            id=salary.pk,
        )
