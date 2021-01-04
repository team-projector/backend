from jnt_django_graphene_toolbox.errors import GraphQLPermissionDenied

from tests.test_payroll.factories import BonusFactory
from tests.test_users.factories import UserFactory


def test_query(user, gql_client, gql_raw):
    """
    Test query.

    :param user:
    :param gql_client:
    """
    bonus = BonusFactory(user=user)
    gql_client.set_user(user)

    response = gql_client.execute(
        gql_raw("bonus"),
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

    response = bonus_query(
        root=None,
        info=ghl_mock_info,
        id=bonus.pk,
    )
    assert isinstance(response, GraphQLPermissionDenied)


def test_not_found(ghl_auth_mock_info, bonus_query):
    """
    Test not found.

    :param ghl_auth_mock_info:
    :param bonus_query:
    """
    response = bonus_query(
        root=None,
        info=ghl_auth_mock_info,
        id=1,
    )
    assert response is None


def test_not_allowed_for_user(user, bonus_query, ghl_auth_mock_info):
    """
    Test not allowed for user.

    :param user:
    :param bonus_query:
    :param ghl_auth_mock_info:
    """
    bonus = BonusFactory.create(user=UserFactory.create())
    response = bonus_query(
        root=None,
        info=ghl_auth_mock_info,
        id=bonus.pk,
    )

    assert response is None
