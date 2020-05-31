# -*- coding: utf-8 -*-

from bitfield import BitField
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.development.models.managers import TeamMemberManager


class TeamMemberRole(models.TextChoices):
    """Team member roles choices."""

    LEADER = "LEADER", _("CH__LEADER")  # noqa: WPS115
    DEVELOPER = "DEVELOPER", _("CH__DEVELOPER")  # noqa: WPS115
    WATCHER = "WATCHER", _("CH__WATCHER")  # noqa: WPS115


class TeamMember(models.Model):
    """The team member model."""

    class Meta:
        verbose_name = _("VN__TEAM_MEMBER")
        verbose_name_plural = _("VN__TEAM_MEMBERS")
        unique_together = ("team", "user")

    roles = BitField(flags=TeamMemberRole.choices, default=0)

    team = models.ForeignKey(
        "Team",
        models.CASCADE,
        verbose_name=_("VN__TEAM"),
        help_text=_("HT__TEAM"),
    )

    user = models.ForeignKey(  # noqa: CCE001
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        verbose_name=_("VN__USER"),
        help_text=_("HT__USER"),
    )

    objects = TeamMemberManager()  # noqa: WPS110

    def __str__(self):
        """Returns object string representation."""
        return "{0}: {1}".format(self.team, self.user)
