# -*- coding: utf-8 -*-

from pytest import raises

from apps.core.graphql.errors import GraphQLNotFound, GraphQLPermissionDenied
from tests.test_payroll.factories import BonusFactory
from tests.test_users.factories import UserFactory

GHL_QUERY_BONUS = """
query ($id: ID!) {
  bonus (id: $id) {
    id
    description
  }
}
"""


def test_query(user, ghl_client):
    bonus = BonusFactory(user=user)
    ghl_client.set_user(user)

    response = ghl_client.execute(
        GHL_QUERY_BONUS,
        variable_values={
            "id": bonus.pk,
        },
    )

    assert "errors" not in response
    assert response["data"]["bonus"]["id"] == str(bonus.pk)


def test_unauth(db, ghl_mock_info, bonus_query, user):
    bonus = BonusFactory(user=user)

    with raises(GraphQLPermissionDenied):
        bonus_query(
            root=None,
            info=ghl_mock_info,
            id=bonus.pk,
        )


def test_not_found(ghl_auth_mock_info, bonus_query):
    with raises(GraphQLNotFound):
        bonus_query(
            root=None,
            info=ghl_auth_mock_info,
            id=1,
        )


def test_not_allowed_for_user(user, bonus_query, ghl_auth_mock_info):
    bonus = BonusFactory(user=UserFactory())
    with raises(GraphQLNotFound):
        bonus_query(
            root=None,
            info=ghl_auth_mock_info,
            id=bonus.pk,
        )