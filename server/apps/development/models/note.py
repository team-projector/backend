from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.utils import Choices
from apps.users.models import User
from ..db.managers import NoteManager


class Note(models.Model):
    TYPE = Choices(
        ('time_spend', 'Time spend'),
        ('reset_spend', 'Reset spend')
    )

    object_id = models.IntegerField()
    content_object = GenericForeignKey()
    content_type = models.ForeignKey(ContentType, models.CASCADE)

    gl_id = models.PositiveIntegerField(
        verbose_name=_('VN__GITLAB_ID'),
        help_text=_('HT__GITLAB_ID')
    )

    user = models.ForeignKey(
        User,
        models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('VN__USER'),
        help_text=_('HT__USER')
    )

    created_at = models.DateTimeField(
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        null=True,
        blank=True
    )

    body = models.TextField(null=True)

    type = models.CharField(
        choices=TYPE,
        max_length=20,
        verbose_name=_('VN__TYPE'),
        help_text=_('HT__TYPE')
    )

    data = JSONField(encoder=DjangoJSONEncoder)

    objects = NoteManager()

    class Meta:
        verbose_name = _('VN__NOTE')
        verbose_name_plural = _('VN__NOTES')
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user} [{self.created_at:%x}]: {self.type}'
