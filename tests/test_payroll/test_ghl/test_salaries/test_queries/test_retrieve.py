# -*- coding: utf-8 -*-

import pytest
from jnt_django_graphene_toolbox.errors import (
    GraphQLNotFound,
    GraphQLPermissionDenied,
)

from tests.test_payroll.factories import SalaryFactory
from tests.test_users.factories import UserFactory

GHL_QUERY_SALARY = """
query ($id: ID!) {
  salary (id: $id) {
    id
    comment
  }
}
"""


def test_query(user, ghl_client):
    salary = SalaryFactory(user=user)
    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_SALARY, variable_values={"id": salary.pk},
    )

    assert "errors" not in response
    assert response["data"]["salary"]["id"] == str(salary.pk)


def test_unauth(ghl_mock_info, salary_query, user):
    salary = SalaryFactory(user=user)

    with pytest.raises(GraphQLPermissionDenied):
        salary_query(
            root=None, info=ghl_mock_info, id=salary.pk,
        )


def test_not_found(ghl_auth_mock_info, salary_query):
    with pytest.raises(GraphQLNotFound):
        salary_query(
            root=None, info=ghl_auth_mock_info, id=1,
        )


def test_not_allowed_for_user(user, salary_query, ghl_auth_mock_info):
    salary = SalaryFactory(user=UserFactory())
    with pytest.raises(GraphQLNotFound):
        salary_query(
            root=None, info=ghl_auth_mock_info, id=salary.pk,
        )
