from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from pytest import raises
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.settings import api_settings

from apps.users.rest.authentication import TokenAuthentication
from apps.users.services.token import create_user_token


def test_no_auth(user, client):
    assert TokenAuthentication in api_settings.DEFAULT_AUTHENTICATION_CLASSES

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
