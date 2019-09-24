# -*- coding: utf-8 -*-

from bitfield import BitField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.utils import Choices
from apps.users.models.managers import UserManager

USER_ROLES = Choices(
    ('developer', _('CH_DEVELOPER')),
    ('team_leader', _('CH_TEAM_LEADER')),
    ('project_manager', _('CH_PROJECT_MANAGER')),
    ('customer', _('CH_CUSTOMER')),
    ('shareholder', _('CH_SHAREHOLDER')),
)


class User(AbstractBaseUser, PermissionsMixin):
    USERNAME_FIELD = 'login'  # noqa WPS115

    login = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        unique=True,
        verbose_name=_('VN__LOGIN'),
        help_text=_('HT__LOGIN'),
    )

    name = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        unique=True,
        verbose_name=_('VN__NAME'),
        help_text=_('HT__NAME'),
    )

    email = models.EmailField(
        max_length=150,
        null=True,
        blank=True,
        unique=True,
        verbose_name=_('VN__EMAIL'),
        help_text=_('HT__EMAIL'),
    )

    hour_rate = models.FloatField(
        default=0,
        verbose_name=_('VN__HOUR_RATE'),
        help_text=_('HT__HOUR_RATE'),
    )

    customer_hour_rate = models.FloatField(
        default=0,
        verbose_name=_('VN__CUSTOMER_HOUR_RATE'),
        help_text=_('HT__CUSTOMER_HOUR_RATE'),
    )

    taxes = models.FloatField(
        default=0,
        verbose_name=_('VN__TAXES'),
        help_text=_('HT__TAXES'),
    )

    roles = BitField(
        flags=USER_ROLES,
        default=0,
    )

    is_staff = models.BooleanField(
        default=True,
        verbose_name=_('VN__IS_STAFF'),
        help_text=_('HT__IS_STAFF'),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('VN__IS_ACTIVE'),
        help_text=_('HT__IS_ACTIVE'),
    )

    gl_avatar = models.URLField(
        null=True,
        blank=True,
        unique=True,
        verbose_name=_('VN__GITLAB_AVATAR'),
        help_text=_('HT__GITLAB_AVATAR'),
    )

    gl_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('VN__GITLAB_ID'),
        help_text=_('HT__GITLAB_ID'),
    )

    gl_url = models.URLField(
        null=True,
        blank=True,
        verbose_name=_('VN__GITLAB_URL'),
        help_text=_('HT__GITLAB_URL'),
    )

    gl_last_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('VN__GITLAB_LAST_SYNC'),
        help_text=_('HT__GITLAB_LAST_SYNC'),
    )

    gl_token = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name=_('VN__PERSONAL_GITLAB_TOKEN'),
        help_text=_('HT__PERSONAL_GITLAB_TOKEN'),
    )

    daily_work_hours = models.PositiveIntegerField(default=8)

    objects = UserManager()

    class Meta:
        verbose_name = _('VN__USER')
        verbose_name_plural = _('VN__USERS')
        ordering = ('login',)

    def __str__(self):
        return self.login

    def get_short_name(self):
        return self.login
