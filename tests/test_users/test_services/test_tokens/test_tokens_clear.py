from datetime import timedelta

from django.test import override_settings
from django.utils import timezone

from apps.users.models import Token


@override_settings(TOKEN_EXPIRE_PERIOD=None)
def test_no_expire(token_service, user):
    """Test if no expiration."""
    token_service.create_user_token(user)

    token_service.clear_tokens()

    assert Token.objects.exists()


@override_settings(TOKEN_EXPIRE_PERIOD=1)
def test_expired_setted(token_service, user):
    """Test with expiration period."""
    token_service.create_user_token(user)

    token_service.clear_tokens()

    assert Token.objects.exists()


@override_settings(TOKEN_EXPIRE_PERIOD=1)
def test_clear_expired(token_service, user):
    """Test with expiration period."""
    token_expired = token_service.create_user_token(user)
    token_expired.created = timezone.now() - timedelta(minutes=3)
    token_expired.save(update_fields=["created"])

    token_service.clear_tokens()

    assert not Token.objects.exists()
