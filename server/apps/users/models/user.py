# -*- coding: utf-8 -*-

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from jnt_django_toolbox.models.fields import BitField

from apps.core.models.validators import tax_rate_validator
from apps.users.models import Position
from apps.users.models.managers import UserManager


class UserRole(models.TextChoices):
    """User roles choices."""

    DEVELOPER = "DEVELOPER", _("CH__DEVELOPER")  # noqa: WPS115
    TEAM_LEADER = "TEAM_LEADER", _("CH__TEAM_LEADER")  # noqa: WPS115
    MANAGER = (  # noqa: WPS115, E501
        "MANAGER",
        _("CH__MANAGER"),
    )
    CUSTOMER = "CUSTOMER", _("CH__CUSTOMER")  # noqa: WPS115
    SHAREHOLDER = "SHAREHOLDER", _("CH__SHAREHOLDER")  # noqa: WPS115


USER_LOGIN_MAX_LENGTH = 150
USER_EMAIL_MAX_LENGTH = 150
USER_GITLAB_TOKEN_MAX_LENGTH = 128


class User(AbstractBaseUser, PermissionsMixin):
    """The User model."""

    class Meta:
        verbose_name = _("VN__USER")
        verbose_name_plural = _("VN__USERS")
        ordering = ("login",)

    USERNAME_FIELD = "login"  # noqa: WPS115

    login = models.CharField(
        max_length=USER_LOGIN_MAX_LENGTH,
        blank=True,
        unique=True,
        verbose_name=_("VN__LOGIN"),
        help_text=_("HT__LOGIN"),
    )

    name = models.CharField(
        max_length=USER_LOGIN_MAX_LENGTH,
        blank=True,
        verbose_name=_("VN__NAME"),
        help_text=_("HT__NAME"),
    )

    email = models.EmailField(
        max_length=USER_EMAIL_MAX_LENGTH,
        blank=True,
        verbose_name=_("VN__EMAIL"),
        help_text=_("HT__EMAIL"),
    )

    hour_rate = models.FloatField(
        default=0,
        verbose_name=_("VN__HOUR_RATE"),
        help_text=_("HT__HOUR_RATE"),
    )

    customer_hour_rate = models.FloatField(
        default=0,
        verbose_name=_("VN__CUSTOMER_HOUR_RATE"),
        help_text=_("HT__CUSTOMER_HOUR_RATE"),
    )

    tax_rate = models.FloatField(
        default=0,
        verbose_name=_("VN__TAX_RATE"),
        help_text=_("HT__TAX_RATE"),
        validators=(tax_rate_validator,),
    )

    annual_paid_work_breaks_days = models.IntegerField(
        default=0,
        verbose_name=_("VN__ANNUAL_PAID_WORK_BREAKS_DAYS"),
        help_text=_("HT__ANNUAL_PAID_WORK_BREAKS_DAYS"),
    )

    roles = BitField(flags=UserRole.choices, default=0)

    is_staff = models.BooleanField(
        default=True,
        verbose_name=_("VN__IS_STAFF"),
        help_text=_("HT__IS_STAFF"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("VN__IS_ACTIVE"),
        help_text=_("HT__IS_ACTIVE"),
    )

    gl_avatar = models.URLField(
        blank=True,
        verbose_name=_("VN__GITLAB_AVATAR"),
        help_text=_("HT__GITLAB_AVATAR"),
    )

    gl_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("VN__GITLAB_ID"),
        help_text=_("HT__GITLAB_ID"),
    )

    gl_url = models.URLField(
        blank=True,
        verbose_name=_("VN__GITLAB_URL"),
        help_text=_("HT__GITLAB_URL"),
    )

    gl_last_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("VN__GITLAB_LAST_SYNC"),
        help_text=_("HT__GITLAB_LAST_SYNC"),
    )

    gl_token = models.CharField(
        max_length=USER_GITLAB_TOKEN_MAX_LENGTH,
        blank=True,
        verbose_name=_("VN__PERSONAL_GITLAB_TOKEN"),
        help_text=_("HT__PERSONAL_GITLAB_TOKEN"),
    )

    notify_pipeline_status = models.BooleanField(
        default=False,
        verbose_name=_("VN__NOTIFY_PIPELINE_STATUS"),
        help_text=_("HT__NOTIFY_PIPELINE_STATUS"),
    )

    daily_work_hours = models.PositiveIntegerField(default=8)

    position = models.ForeignKey(  # noqa: CCE001
        Position,
        models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("VN__POSITION"),
        help_text=_("HT__POSITION"),
    )

    objects = UserManager()  # noqa: WPS110

    def __str__(self):
        """Returns object string representation."""
        return self.login

    def get_short_name(self):
        """Return the short name for the user."""
        return self.login
