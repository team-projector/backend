from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from ..models import Token, User


def create_user_token(user: User) -> Token:
    return Token.objects.create(user=user)


def clear_tokens() -> None:
    if settings.TOKEN_EXPIRE_PERIOD is None:
        return

    Token.objects.filter(
        created__lt=timezone.now() -  # noqa W504
                    timedelta(minutes=settings.TOKEN_EXPIRE_PERIOD),
    ).delete()
