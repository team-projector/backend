import pytest
from jnt_django_graphene_toolbox.errors import (
    GraphQLNotFound,
    GraphQLPermissionDenied,
)

from tests.test_payroll.factories import BonusFactory
from tests.test_users.factories import UserFactory


def test_query(user, ghl_client, ghl_raw):
    """
    Test query.

    :param user:
    :param ghl_client:
    """
    bonus = BonusFactory(user=user)
    ghl_client.set_user(user)

    response = ghl_client.execute(
        ghl_raw("bonus"),
        variable_values={"id": bonus.pk},
    )

    assert "errors" not in response
    assert response["data"]["bonus"]["id"] == str(bonus.pk)


def test_unauth(db, ghl_mock_info, bonus_query, user):
    """
    Test unauth.

    :param db:
    :param ghl_mock_info:
    :param bonus_query:
    :param user:
    """
    bonus = BonusFactory(user=user)

    with pytest.raises(GraphQLPermissionDenied):
        bonus_query(
            root=None,
            info=ghl_mock_info,
            id=bonus.pk,
        )


def test_not_found(ghl_auth_mock_info, bonus_query):
    """
    Test not found.

    :param ghl_auth_mock_info:
    :param bonus_query:
    """
    with pytest.raises(GraphQLNotFound):
        bonus_query(
            root=None,
            info=ghl_auth_mock_info,
            id=1,
        )


def test_not_allowed_for_user(user, bonus_query, ghl_auth_mock_info):
    """
    Test not allowed for user.

    :param user:
    :param bonus_query:
    :param ghl_auth_mock_info:
    """
    bonus = BonusFactory(user=UserFactory())
    with pytest.raises(GraphQLNotFound):
        bonus_query(
            root=None,
            info=ghl_auth_mock_info,
            id=bonus.pk,
        )
