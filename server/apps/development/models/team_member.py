from bitfield import BitField
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.utils import Choices
from apps.users.models import User
from .team import Team


class TeamMember(models.Model):
    ROLES = Choices(
        ('leader', _('CH_LEADER')),
        ('developer', _('CH_DEVELOPER')),
        ('watcher', _('CH_WATCHER')),
    )

    team = models.ForeignKey(
        Team, models.CASCADE,
        related_name='members',
        verbose_name=_('VN__TEAM'),
        help_text=_('HT__TEAM')
    )

    user = models.ForeignKey(
        User, models.CASCADE,
        related_name='team_members',
        verbose_name=_('VN__USER'),
        help_text=_('HT__USER')
    )

    roles = BitField(
        flags=ROLES,
        default=0
    )

    class Meta:
        verbose_name = _('VN__TEAM_MEMBER')
        verbose_name_plural = _('VN__TEAM_MEMBERS')
        ordering = ('team', 'user')
        unique_together = ('team', 'user')

    def __str__(self):
        return f'{self.team}: {self.user}'
