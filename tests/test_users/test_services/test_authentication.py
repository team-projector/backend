from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from pytest import raises
from rest_framework.exceptions import AuthenticationFailed

from apps.core.graphql.security.authentication import TokenAuthentication
from apps.users.models import Token
from apps.users.services import token as token_service
from apps.users.services import user as user_service
from tests.fixtures.users import DEFAULT_USER_PASSWORD


def test_login_user(user):
    assert Token.objects.count() == 0

    token = user_service.login_user(user.login, DEFAULT_USER_PASSWORD, None)

    assert token is not None
    assert Token.objects.count() == 1


def test_login_user_not_active(user):
    user.is_active = False
    user.save()

    with raises(AuthenticationFailed):
        user_service.login_user(user.login, DEFAULT_USER_PASSWORD, None)


def test_login_invalid_password(user):
    with raises(AuthenticationFailed):
        user_service.login_user(user.login, f'{DEFAULT_USER_PASSWORD}bla', None)


def test_login_empty_password(user):
    with raises(AuthenticationFailed):
        user_service.login_user(user.login, '', None)


def test_login_user_invalid_login(user):
    with raises(AuthenticationFailed):
        user_service.login_user(f'{user.login}bla', DEFAULT_USER_PASSWORD, None)


def test_login_empty_user(user):
    with raises(AuthenticationFailed):
        user_service.login_user('', DEFAULT_USER_PASSWORD, None)


def test_multitokens(user):
    assert Token.objects.count() == 0

    user_service.login_user(user.login, DEFAULT_USER_PASSWORD, None)

    assert Token.objects.filter(user=user).count() == 1

    user_service.login_user(user.login, DEFAULT_USER_PASSWORD, None)

    assert Token.objects.filter(user=user).count() == 2


def test_no_auth(user, client):
    client.user = user
    request = client.get('/')

    assert Token.objects.filter(user=user).exists() is False
    assert TokenAuthentication().authenticate(request) is None


def test_auth(user, client):
    token = token_service.create_user_token(user)

    client.set_credentials(user, token)
    request = client.get('/')

    assert TokenAuthentication().authenticate(request) is not None


def test_expired_token(user, client):
    token = token_service.create_user_token(user)
    token.created = timezone.now() - timedelta(
        minutes=settings.TOKEN_EXPIRE_PERIOD + 60
    )
    token.save()

    client.set_credentials(user, token)
    request = client.get('/')

    with raises(AuthenticationFailed) as error:
        TokenAuthentication().authenticate(request)
        assert str(error.value) == 'Token has expired'


def test_invalid_token(user, client):
    token = token_service.create_user_token(user)
    token.key += '123456'

    client.set_credentials(user, token)
    request = client.get('/')

    with raises(AuthenticationFailed) as error:
        TokenAuthentication().authenticate(request)
        assert str(error.value) == 'Invalid token.'
