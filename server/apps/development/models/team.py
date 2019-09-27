# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core import consts
from .team_member import TeamMember


class Team(models.Model):
    title = models.CharField(
        max_length=consts.FIELD_LEN255,
        verbose_name=_('VN__TITLE'),
        help_text=_('HT__TITLE'),
        unique=True,
    )

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through=TeamMember,
        related_name='teams',
    )

    class Meta:
        verbose_name = _('VN__TEAM')
        verbose_name_plural = _('VN__TEAMS')
        ordering = ('title',)

    def __str__(self):
        return self.title
