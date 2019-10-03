# -*- coding: utf-8 -*-

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.utils import Choices
from apps.users.models import User

from .managers import NoteManager

NOTE_TYPES = Choices(
    ('time_spend', 'Time spend'),
    ('reset_spend', 'Reset spend'),
    ('moved_from', 'Moved from'),
)

NOTE_TYPE_MAX_LENGTH = 20


class Note(models.Model):
    """
    The milestone model.

    Fill from Gitlab when loading issues or merge requests.
    """
    object_id = models.IntegerField()

    content_object = GenericForeignKey()

    content_type = models.ForeignKey(
        ContentType,
        models.CASCADE,
    )

    gl_id = models.PositiveIntegerField(
        verbose_name=_('VN__GITLAB_ID'),
        help_text=_('HT__GITLAB_ID'),
    )

    user = models.ForeignKey(
        User,
        models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('VN__USER'),
        help_text=_('HT__USER'),
    )

    created_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    body = models.TextField(
        null=True,
    )

    type = models.CharField(
        choices=NOTE_TYPES,
        max_length=NOTE_TYPE_MAX_LENGTH,
        verbose_name=_('VN__TYPE'),
        help_text=_('HT__TYPE'),
    )

    data = JSONField(
        encoder=DjangoJSONEncoder,
    )

    objects = NoteManager()

    class Meta:
        verbose_name = _('VN__NOTE')
        verbose_name_plural = _('VN__NOTES')
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user} [{self.created_at}]: {self.type}'
