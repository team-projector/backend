from datetime import datetime
from typing import Optional

from django.conf import settings
from django.db import models
from django.db.models import Max
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from apps.core.models.mixins import GitlabEntityMixin, GitlabInternalIdMixin
from apps.core.models.utils import Choices
from apps.payroll.models.mixins import SpentTimesMixin
from .managers import MergeRequestManager
from .mixins import NotableMixin

STATE_CLOSED = 'closed'
STATE_OPENED = 'opened'
STATE_MERGED = 'merged'


class MergeRequest(NotableMixin,
                   SpentTimesMixin,
                   GitlabEntityMixin,
                   GitlabInternalIdMixin):
    STATE = Choices(
        (STATE_OPENED, 'closed'),
        (STATE_MERGED, 'merged'),
        (STATE_CLOSED, 'opened')
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
        'development.Label',
        related_name='merge_requests',
        blank=True
    )

    project = models.ForeignKey(
        'development.Project',
        models.SET_NULL,
        null=True,
        blank=True,
        related_name='merge_requests',
        verbose_name=_('VN__PROJECT'),
        help_text=_('HT__PROJECT')
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        related_name='merge_requests',
        null=True,
        blank=True,
        verbose_name=_('VN__USER'),
        help_text=_('HT__USER')
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        related_name='author_merge_requests',
        null=True,
        blank=True,
        verbose_name=_('VN__AUTHOR'),
        help_text=_('HT__AUTHOR')
    )

    milestone = models.ForeignKey(
        'development.Milestone',
        models.CASCADE,
        null=True,
        blank=True,
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='participant_merge_requests',
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

    @property
    def time_remains(self) -> Optional[int]:
        if self.time_estimate is not None and self.total_time_spent is not None:
            return max(self.time_estimate - self.total_time_spent, 0)

    @property
    def efficiency(self) -> Optional[float]:
        if self.efficiency_available:
            return self.time_estimate / self.total_time_spent

    @property
    def efficiency_available(self) -> bool:
        return (
            self.state == self.STATE.closed and
            self.total_time_spent and
            self.time_estimate
        )
