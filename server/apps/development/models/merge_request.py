# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from apps.core.consts import DEFAULT_TITLE_LENGTH
from apps.core.models.mixins import GitlabEntityMixin, GitlabInternalIdMixin
from apps.core.models.utils import Choices
from apps.development.models.managers import MergeRequestManager
from apps.development.models.mixins import TrackableMixin

MERGE_REQUESTS_STATES = Choices(
    ('OPENED', _('CH_OPENED')),
    ('MERGED', _('CH_MERGED')),
    ('CLOSED', _('CH_CLOSED')),
)

MERGE_REQUESTS_STATE_MAX_LENGTH = 255


class MergeRequest(
    TrackableMixin,
    GitlabEntityMixin,
    GitlabInternalIdMixin,
):
    """
    The merge request model.

    Fill from Gitlab.
    """

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
        choices=MERGE_REQUESTS_STATES,
        max_length=MERGE_REQUESTS_STATE_MAX_LENGTH,
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

    labels = models.ManyToManyField(
        'development.Label',
        related_name='merge_requests',
        blank=True,
    )

    project = models.ForeignKey(
        'development.Project',
        models.SET_NULL,
        null=True,
        blank=True,
        related_name='merge_requests',
        verbose_name=_('VN__PROJECT'),
        help_text=_('HT__PROJECT'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        related_name='merge_requests',
        null=True,
        blank=True,
        verbose_name=_('VN__USER'),
        help_text=_('HT__USER'),
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        related_name='author_merge_requests',
        null=True,
        blank=True,
        verbose_name=_('VN__AUTHOR'),
        help_text=_('HT__AUTHOR'),
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

    objects = MergeRequestManager()  # noqa WPS110

    class Meta:
        verbose_name = _('VN__MERGE_REQUEST')
        verbose_name_plural = _('VN__MERGE_REQUESTS')
        ordering = ('-created_at',)

    def __str__(self):
        """Returns object string representation."""
        return self.title

    @cached_property
    def last_note_date(self) -> datetime:
        """Returns last note date."""
        return self.notes.aggregate(
            last_created=models.Max('created_at'),
        )['last_created']

    @property
    def time_remains(self) -> Optional[int]:
        """Return the difference between estimate and spent time."""
        if self.time_estimate is not None and self.total_time_spent is not None:
            return max(self.time_estimate - self.total_time_spent, 0)

    @property
    def efficiency(self) -> Optional[float]:
        """
        Return ratio of estimate.

        And spent time only for closed merge requests.
        """
        if self.efficiency_available:
            return self.time_estimate / self.total_time_spent

    @property
    def efficiency_available(self) -> bool:
        """Helper for efficiency method."""
        return (
            self.state == MERGE_REQUESTS_STATES.CLOSED
            and self.total_time_spent
            and self.time_estimate
        )
