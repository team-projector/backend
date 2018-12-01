import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.users.models import Token


def get_user_token(user):
    return Token.objects.create(user=user)


def clear_tokens():
    expire_minutes = getattr(settings, 'REST_FRAMEWORK_TOKEN_EXPIRE_MINUTES', None)

    if expire_minutes is None:
        logging.warning('clear_tokens: REST_FRAMEWORK_TOKEN_EXPIRE_MINUTES is None, clear tokens is not possible')
        return

    Token.objects.filter(created__lt=timezone.now() - timedelta(minutes=expire_minutes)).delete()
