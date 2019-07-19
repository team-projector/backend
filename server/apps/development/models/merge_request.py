from datetime import datetime

from django.db import models
from django.db.models import Max
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from apps.core.db.mixins import GitlabEntityMixin, GitlabInternalIdMixin
from apps.core.db.utils import Choices
from apps.payroll.db.mixins import SpentTimesMixin
from apps.users.models import User
from .label import Label
from .project import Project
from ..db.managers import MergeRequestManager
from ..db.mixins import NotableMixin


class MergeRequest(NotableMixin,
                   SpentTimesMixin,
                   GitlabEntityMixin,
                   GitlabInternalIdMixin):
    STATE = Choices(
        ('closed', 'closed'),
        ('merged', 'merged'),
        ('opened', 'opened')
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_('VN__TITLE'),
        help_text=_('HT__TITLE')
    )

    time_estimate = models.PositiveIntegerField(
        null=True,
        verbose_name=_('VN__TIME_ESTIMATE'),
        help_text=_('HT__TIME_ESTIMATE')
    )

    total_time_spent = models.PositiveIntegerField(
        null=True,
        verbose_name=_('VN__TOTAL_TIME_SPENT'),
        help_text=_('HT__TOTAL_TIME_SPENT')
    )

    state = models.CharField(
        choices=STATE,
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('VN__STATE'),
        help_text=_('HT__STATE')
    )

    created_at = models.DateTimeField(
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        null=True,
        blank=True
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    labels = models.ManyToManyField(
        Label,
        related_name='merge_requests',
        blank=True
    )

    project = models.ForeignKey(
        Project,
        models.SET_NULL,
        null=True,
        blank=True,
        related_name='merge_requests',
        verbose_name=_('VN__PROJECT'),
        help_text=_('HT__PROJECT')
    )

    assignee = models.ForeignKey(
        User,
        models.SET_NULL,
        related_name='assignee_merge_requests',
        null=True,
        blank=True,
        verbose_name=_('VN__ASSIGNEE'),
        help_text=_('HT__ASSIGNEE')
    )

    author = models.ForeignKey(
        User,
        models.SET_NULL,
        related_name='author_merge_requests',
        null=True,
        blank=True,
        verbose_name=_('VN__AUTHOR'),
        help_text=_('HT__AUTHOR')
    )

    milestone = models.ForeignKey(
        'Milestone',
        models.CASCADE,
        null=True,
        blank=True,
    )

    objects = MergeRequestManager()

    class Meta:
        verbose_name = _('VN__MERGE_REQUEST')
        verbose_name_plural = _('VN__MERGE_REQUESTS')
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    @cached_property
    def last_note_date(self) -> datetime:
        return self.notes.aggregate(
            last_created=Max('created_at')
        )['last_created']
