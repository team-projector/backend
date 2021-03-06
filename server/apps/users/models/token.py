from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token as BaseToken


class Token(BaseToken):
    """The authorization token model."""

    class Meta:
        verbose_name = _("VN__TOKEN")
        verbose_name_plural = _("VN__TOKENS")
        ordering = ("-created",)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
