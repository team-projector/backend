# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.mixins import Timestamps
from apps.core.models.utils import Choices

PROJECT_MEMBER_ROLES = Choices(
    ('developer', _('CH_DEVELOPER')),
    ('project_manager', _('CH_PM')),
    ('customer', _('CH_CUSTOMER')),
)


class ProjectMember(Timestamps):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
    )

    role = models.CharField(
        choices=PROJECT_MEMBER_ROLES,
        max_length=20,
        verbose_name=_('VN__ROLE'),
        help_text=_('HT__ROLE'),
    )

    owner = GenericForeignKey()

    content_type = models.ForeignKey(
        ContentType,
        models.CASCADE,
        null=True,
    )

    object_id = models.PositiveIntegerField(
        null=True,
    )

    class Meta:
        verbose_name = _('VN__PROJECT_MEMBER')
        verbose_name_plural = _('VN__PROJECT_MEMBERS')
        unique_together = ('user', 'role', 'object_id')
