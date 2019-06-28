from bitfield import BitField
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.utils import Choices


class TeamMember(models.Model):
    ROLES = Choices(
        ('leader', _('CH_LEADER')),
        ('developer', _('CH_DEVELOPER')),
        ('watcher', _('CH_WATCHER')),
    )

    team = models.ForeignKey(
        'Team',
        models.CASCADE,
        verbose_name=_('VN__TEAM'),
        help_text=_('HT__TEAM')
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
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
        unique_together = ('team', 'user')

    def __str__(self):
        return f'{self.team}: {self.user}'
