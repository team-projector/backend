# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token as BaseToken

from .user import User


class Token(BaseToken):
    """
    The authorization token model.
    """
    user = models.ForeignKey(
        User,
        models.CASCADE,
    )

    class Meta:
        verbose_name = _('VN__TOKEN')
        verbose_name_plural = _('VN__TOKENS')
