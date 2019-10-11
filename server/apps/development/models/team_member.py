# -*- coding: utf-8 -*-

from bitfield import BitField
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.utils import Choices
from apps.development.models.managers import TeamMemberManager

TEAM_MEMBER_ROLES = Choices(
    ('leader', _('CH_LEADER')),
    ('developer', _('CH_DEVELOPER')),
    ('watcher', _('CH_WATCHER')),
)


class TeamMember(models.Model):
    """The team member model."""

    team = models.ForeignKey(
        'Team',
        models.CASCADE,
        verbose_name=_('VN__TEAM'),
        help_text=_('HT__TEAM'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        verbose_name=_('VN__USER'),
        help_text=_('HT__USER'),
    )

    roles = BitField(
        flags=TEAM_MEMBER_ROLES,
        default=0,
    )

    objects = TeamMemberManager()  # noqa WPS110

    class Meta:
        verbose_name = _('VN__TEAM_MEMBER')
        verbose_name_plural = _('VN__TEAM_MEMBERS')
        unique_together = ('team', 'user')

    def __str__(self):
        """Returns object string representation."""
        return f'{self.team}: {self.user}'
