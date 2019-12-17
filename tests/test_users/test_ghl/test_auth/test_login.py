# -*- coding: utf-8 -*-

from pytest import raises
from rest_framework.exceptions import AuthenticationFailed

from apps.users.models import Token
from tests.fixtures.users import DEFAULT_USERNAME, DEFAULT_USER_PASSWORD

GHL_QUERY_LOGIN = """
mutation ($login: String!, $password: String!) {
    login(login: $login, password: $password) {
        token {
          key
        }
    }
}
"""


def test_query(user, ghl_client):
    """Test login raw query."""
    assert not Token.objects.filter(user=user).exists()

    response = ghl_client.execute(
        GHL_QUERY_LOGIN,
        variables={
            'login': DEFAULT_USERNAME,
            'password': DEFAULT_USER_PASSWORD,
        },
    )

    assert 'errors' not in response

    token = Token.objects.filter(user=user).first()
    assert token is not None
    assert response['data']['login']['token']['key'] == token.key


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

    with raises(AuthenticationFailed):
        login_mutation(
            None,
            ghl_mock_info,
            login='wrong{0}'.format(DEFAULT_USERNAME),
            password=DEFAULT_USER_PASSWORD,
        )

    assert not Token.objects.filter(user=user).exists()


def test_wrong_password(user, ghl_mock_info, login_mutation):
    """Test wrong password case."""
    assert not Token.objects.filter(user=user).exists()

    with raises(AuthenticationFailed):
        login_mutation(
            None,
            ghl_mock_info,
            login=DEFAULT_USERNAME,
            password='wrong{0}'.format(DEFAULT_USER_PASSWORD),
        )

    assert not Token.objects.filter(user=user).exists()
