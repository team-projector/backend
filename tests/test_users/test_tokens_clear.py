from datetime import timedelta

from django.test import override_settings
from django.utils import timezone

from apps.users.services.token import create_user_token, clear_tokens
from apps.users.models import Token
from apps.users.tasks import clear_expired_tokens


@override_settings(TOKEN_EXPIRE_PERIOD=None)
def test_settings_token_expire_none(user):
    create_user_token(user)

    clear_tokens()

    assert Token.objects.first() is not None


@override_settings(TOKEN_EXPIRE_PERIOD=1)
def test_clear_tokens(user):
    token_expired = create_user_token(user)
    token_expired.created = timezone.now() - timedelta(minutes=3)
    token_expired.save(update_fields=['created'])

    token_fresh = create_user_token(user)

    clear_tokens()

    assert Token.objects.count() == 1
    assert Token.objects.first() == token_fresh


@override_settings(TOKEN_EXPIRE_PERIOD=1)
def test_task_clear_expired_tokens(user):
    token_expired = create_user_token(user)
    token_expired.created = timezone.now() - timedelta(minutes=3)
    token_expired.save(update_fields=['created'])

    token_fresh = create_user_token(user)

    clear_expired_tokens()

    assert Token.objects.count() == 1
    assert Token.objects.first() == token_fresh
