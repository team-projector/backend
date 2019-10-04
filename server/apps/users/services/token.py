# -*- coding: utf-8 -*-

from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from ..models import Token, User


def create_user_token(user: User) -> Token:
    return Token.objects.create(user=user)


def clear_tokens() -> None:
    if settings.TOKEN_EXPIRE_PERIOD is None:
        return

    created = timezone.now() - timedelta(minutes=settings.TOKEN_EXPIRE_PERIOD)

    Token.objects.filter(created__lt=created).delete()
