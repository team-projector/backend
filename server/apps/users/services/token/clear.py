# -*- coding: utf-8 -*-

from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.users.models import Token


def clear_tokens() -> None:
    """Deletes expired tokens."""
    if settings.TOKEN_EXPIRE_PERIOD is None:
        return

    created = timezone.now() - timedelta(minutes=settings.TOKEN_EXPIRE_PERIOD)

    Token.objects.filter(created__lt=created).delete()
