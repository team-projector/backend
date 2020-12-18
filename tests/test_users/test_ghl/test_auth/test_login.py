from jnt_django_graphene_toolbox.errors import GraphQLInputError

from apps.core.graphql.errors import ApplicationGraphQLError
from apps.users.application.use_cases.users.login import AuthenticationError
from apps.users.models import Token
from tests.fixtures.users import DEFAULT_USER_PASSWORD, DEFAULT_USERNAME


def test_query(user, ghl_client, ghl_raw):
    """Test login raw query."""
    assert not Token.objects.filter(user=user).exists()

    response = ghl_client.execute(
        ghl_raw("login"),
        variable_values={
            "login": DEFAULT_USERNAME,
            "password": DEFAULT_USER_PASSWORD,
        },
    )

    assert "errors" not in response

    token = Token.objects.filter(user=user).first()
    assert token is not None
    assert response["data"]["login"]["token"]["key"] == token.key


def test_success(user, ghl_mock_info, login_mutation):
    """Test success login."""
    assert not Token.objects.filter(user=user).exists()

    response = login_mutation(
        root=None,
        info=ghl_mock_info,
        login=DEFAULT_USERNAME,
        password=DEFAULT_USER_PASSWORD,
    )

    assert Token.objects.filter(pk=response.token.pk, user=user).exists()


def test_wrong_username(user, ghl_mock_info, login_mutation):
    """Test wrong username case."""
    assert not Token.objects.filter(user=user).exists()

    response = login_mutation(
        None,
        ghl_mock_info,
        login="wrong{0}".format(DEFAULT_USERNAME),
        password=DEFAULT_USER_PASSWORD,
    )

    assert isinstance(response, ApplicationGraphQLError)
    assert response.original_error.code == AuthenticationError.code
    assert not Token.objects.filter(user=user).exists()


def test_wrong_password(user, ghl_mock_info, login_mutation):
    """Test wrong password case."""
    assert not Token.objects.filter(user=user).exists()

    response = login_mutation(
        None,
        ghl_mock_info,
        login=DEFAULT_USERNAME,
        password="wrong{0}".format(DEFAULT_USER_PASSWORD),
    )

    assert isinstance(response, ApplicationGraphQLError)
    assert response.original_error.code == AuthenticationError.code
    assert not Token.objects.filter(user=user).exists()


def test_empty_credentials(user, ghl_mock_info, login_mutation):
    """Test empty credentials."""
    assert not Token.objects.filter(user=user).exists()

    response = login_mutation(
        None,
        ghl_mock_info,
        login="",
        password="",
    )

    assert isinstance(response, GraphQLInputError)
    assert not Token.objects.filter(user=user).exists()
