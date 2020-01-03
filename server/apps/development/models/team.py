# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.consts import DEFAULT_TITLE_LENGTH
from apps.development.models.team_member import TeamMember


class Team(models.Model):
    """The team model."""

    title = models.CharField(
        max_length=DEFAULT_TITLE_LENGTH,
        verbose_name=_("VN__TITLE"),
        help_text=_("HT__TITLE"),
        unique=True,
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through=TeamMember,
        related_name="teams",
    )

    class Meta:
        verbose_name = _("VN__TEAM")
        verbose_name_plural = _("VN__TEAMS")
        ordering = ("title",)

    def __str__(self):
        """Returns object string representation."""
        return self.title
