from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.mixins import GitlabEntityMixin, GitlabInternalIdMixin, Timestamps
from ..db.managers import MilestoneManager


class Milestone(GitlabEntityMixin,
                GitlabInternalIdMixin,
                Timestamps):
    title = models.CharField(
        max_length=255,
        verbose_name=_('VN__TITLE'),
        help_text=_('HT__TITLE')
    )
    description = models.TextField(
        verbose_name=_('VN__DESCRIPTION'),
        help_text=_('HT__DESCRIPTION')
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('VN__START_DATE'),
        help_text=_('HT__START_DATE')
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('VN__DUE_DATE'),
        help_text=_('HT__DUE_DATE')
    )
    budget = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2,
        verbose_name=_('VN__BUDGET'),
        help_text=_('HT__BUDGET')
    )

    owner = GenericForeignKey()
    content_type = models.ForeignKey(
        ContentType,
        models.CASCADE
    )
    object_id = models.PositiveIntegerField()

    objects = MilestoneManager()

    class Meta:
        verbose_name = _('VN__MILESTONE')
        verbose_name_plural = _('VN__MILESTONES')
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.title} ({self.owner})'
