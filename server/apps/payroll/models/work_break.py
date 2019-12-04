# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.mixins import Timestamps
from apps.core.models.utils import Choices
from apps.payroll.models.managers import WorkBreakManager
from apps.payroll.models.mixins import ApprovedMixin

WORK_BREAK_REASONS = Choices(
    ('DAYOFF', _('CH_DAYOFF')),
    ('VACATION', _('CH_VACATION')),
    ('DISEASE', _('CH_DISEASE')),
)

WORK_BREAK_REASON_MAX_LENGTH = 15


class WorkBreak(ApprovedMixin, Timestamps):
    """The work break model."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        related_name='work_break',
        verbose_name=_('VN__USER'),
        help_text=_('HT__USER'),
    )

    from_date = models.DateTimeField(
        verbose_name=_('VN__DATE_FROM'),
        help_text=_('HT__DATE_FROM'),
    )

    to_date = models.DateTimeField(
        verbose_name=_('VN__DATE_TO'),
        help_text=_('HT__DATE_TO'),
    )

    reason = models.CharField(
        choices=WORK_BREAK_REASONS,
        blank=False,
        max_length=WORK_BREAK_REASON_MAX_LENGTH,
        verbose_name=_('VN__REASON'),
        help_text=_('HT__REASON'),
    )

    comment = models.TextField(
        verbose_name=_('VN__COMMENT'),
        help_text=_('HT__COMMENT'),
    )

    objects = WorkBreakManager()  # noqa: WPS110

    class Meta:
        verbose_name = _('VN__WORKBREAK')
        verbose_name_plural = _('VN__WORKBREAKS')
        ordering = ('-from_date',)

    def __str__(self):
        """Returns object string representation."""
        period = '{0} - {1}'.format(self.from_date, self.to_date)

        return '{0}: {1} ({2})'.format(self.user, self.reason, period)
