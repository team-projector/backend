# -*- coding: utf-8 -*-

import pytest

from apps.core.graphql.errors import GraphQLNotFound, GraphQLPermissionDenied
from tests.test_payroll.factories import PenaltyFactory
from tests.test_users.factories import UserFactory

GHL_QUERY_PENALTY = """
query ($id: ID!) {
  penalty (id: $id) {
    id
    comment
  }
}
"""


def test_query(user, ghl_client):
    penalty = PenaltyFactory(user=user)
    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_PENALTY, variable_values={"id": penalty.pk},
    )

    assert "errors" not in response
    assert response["data"]["penalty"]["id"] == str(penalty.pk)


def test_unauth(db, ghl_mock_info, penalty_query, user):
    penalty = PenaltyFactory(user=user)

    with pytest.raises(GraphQLPermissionDenied):
        penalty_query(
            root=None, info=ghl_mock_info, id=penalty.pk,
        )


def test_not_found(ghl_auth_mock_info, penalty_query):
    with pytest.raises(GraphQLNotFound):
        penalty_query(
            root=None, info=ghl_auth_mock_info, id=1,
        )


def test_not_allowed_for_user(user, penalty_query, ghl_auth_mock_info):
    penalty = PenaltyFactory(user=UserFactory())
    with pytest.raises(GraphQLNotFound):
        penalty_query(
            root=None, info=ghl_auth_mock_info, id=penalty.pk,
        )
