# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional

from django.conf import settings
from django.db import models
from django.db.models import Max
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from apps.core.consts import DEFAULT_TITLE_LENGTH
from apps.core.models.mixins import GitlabEntityMixin, GitlabInternalIdMixin
from apps.core.models.utils import Choices
from apps.payroll.models.mixins import SpentTimesMixin

from .managers import IssueManager
from .mixins import NotableMixin

ISSUE_STATES = Choices(
    ('opened', 'opened'),
    ('closed', 'closed'),
)

ISSUE_STATE_MAX_LENGTH = 255


class Issue(NotableMixin,
            SpentTimesMixin,
            GitlabEntityMixin,
            GitlabInternalIdMixin):
    title = models.CharField(
        max_length=DEFAULT_TITLE_LENGTH,
        verbose_name=_('VN__TITLE'),
        help_text=_('HT__TITLE'),
    )

    time_estimate = models.PositiveIntegerField(
        null=True,
        verbose_name=_('VN__TIME_ESTIMATE'),
        help_text=_('HT__TIME_ESTIMATE'),
    )

    total_time_spent = models.PositiveIntegerField(
        null=True,
        verbose_name=_('VN__TOTAL_TIME_SPENT'),
        help_text=_('HT__TOTAL_TIME_SPENT'),
    )

    state = models.CharField(
        max_length=ISSUE_STATE_MAX_LENGTH,
        null=True,
        blank=True,
        verbose_name=_('VN__STATE'),
        help_text=_('HT__STATE'),
    )

    created_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    closed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    labels = models.ManyToManyField(
        'development.Label',
        related_name='issues',
        blank=True,
    )

    project = models.ForeignKey(
        'development.Project',
        models.SET_NULL,
        null=True,
        blank=True,
        related_name='issues',
        verbose_name=_('VN__PROJECT'),
        help_text=_('HT__PROJECT'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('VN__USER'),
        help_text=_('HT__USER'),
    )

    milestone = models.ForeignKey(
        'development.Milestone',
        models.CASCADE,
        null=True,
        blank=True,
    )

    ticket = models.ForeignKey(
        'development.Ticket',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issues',
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='participant_issues',
    )

    is_merged = models.BooleanField(default=False)

    merge_requests = models.ManyToManyField(
        'development.MergeRequest',
        blank=True,
        related_name='issues',
    )

    objects = IssueManager()

    class Meta:
        verbose_name = _('VN__ISSUE')
        verbose_name_plural = _('VN__ISSUES')
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    @cached_property
    def last_note_date(self) -> datetime:
        return self.notes.aggregate(
            last_created=Max('created_at'),
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
            self.state == ISSUE_STATES.closed
            and self.total_time_spent
            and self.time_estimate
        )
