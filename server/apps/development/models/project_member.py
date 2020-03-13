# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.mixins import Timestamps


class ProjectMemberRole(models.TextChoices):
    """Project member role choices."""

    DEVELOPER = "DEVELOPER", _("CH__DEVELOPER")  # noqa: WPS115
    MANAGER = ("MANAGER", _("CH__MANAGER"))  # noqa: WPS115
    CUSTOMER = "CUSTOMER", _("CH__CUSTOMER")  # noqa: WPS115


PROJECT_MEMBER_ROLE_MAX_LENGTH = 20


class ProjectMember(Timestamps):
    """The project member model."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)

    role = models.CharField(
        choices=ProjectMemberRole.choices,
        max_length=PROJECT_MEMBER_ROLE_MAX_LENGTH,
        verbose_name=_("VN__ROLE"),
        help_text=_("HT__ROLE"),
    )

    owner = GenericForeignKey()
    content_type = models.ForeignKey(ContentType, models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)

    class Meta:
        verbose_name = _("VN__PROJECT_MEMBER")
        verbose_name_plural = _("VN__PROJECT_MEMBERS")
        unique_together = ("user", "role", "object_id")
