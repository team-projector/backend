from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from pytest import raises
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.settings import api_settings

from apps.users.models import Token
from apps.users.rest.authentication import TokenAuthentication
from apps.users.services.token import create_user_token
from apps.users.services.auth import login_user
from tests.base import USER_PASSWORD


def test_login_user(user):
    assert TokenAuthentication in api_settings.DEFAULT_AUTHENTICATION_CLASSES
    assert Token.objects.count() == 0

    token = login_user(user.login, USER_PASSWORD, None)

    assert token is not None
    assert Token.objects.count() == 1


def test_login_user_without_password_or_login(user):
    with raises(AuthenticationFailed):
        login_user(user.login, '', None)

    with raises(AuthenticationFailed):
        login_user('', USER_PASSWORD, None)


def test_login_not_existed_user(user):
    with raises(AuthenticationFailed):
        login_user(user.login, 'test1234', None)


def test_no_auth(user, client):
    client.user = user
    request = client.get('/')

    assert TokenAuthentication().authenticate(request) is None


def test_expired_token(user, client):
    token = create_user_token(user)
    token.created = timezone.now() - timedelta(
        minutes=settings.REST_FRAMEWORK_TOKEN_EXPIRE + 60
    )
    token.save()

    client.set_credentials(user, token)
    request = client.get('/')

    with raises(AuthenticationFailed) as error:
        TokenAuthentication().authenticate(request)

    assert str(error.value) == 'Token has expired'


def test_invalid_token(user, client):
    token = create_user_token(user)
    token.key += '123456'

    client.set_credentials(user, token)
    request = client.get('/')

    with raises(AuthenticationFailed) as error:
        TokenAuthentication().authenticate(request)

    assert str(error.value) == 'Invalid token.'
