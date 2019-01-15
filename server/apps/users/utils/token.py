from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.users.models import Token


def create_user_token(user):
    return Token.objects.create(user=user)


def clear_tokens():
    if settings.REST_FRAMEWORK_TOKEN_EXPIRE is None:
        return

    Token.objects.filter(created__lt=timezone.now() - timedelta(minutes=settings.REST_FRAMEWORK_TOKEN_EXPIRE)).delete()
