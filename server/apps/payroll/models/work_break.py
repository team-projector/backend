from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.mixins import Timestamps
from apps.core.models.utils import Choices
from apps.payroll.models.managers import WorkBreakManager
from apps.payroll.models.mixins import ApprovedMixin

WORK_BREAK_REASONS = Choices(
    ('dayoff', _('CH_DAYOFF')),
    ('vacation', _('CH_VACATION')),
    ('disease', _('CH_DISEASES')),
)


class WorkBreak(ApprovedMixin, Timestamps):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        related_name='work_break',
        verbose_name=_('VN__USER'),
        help_text=_('HT__USER')
    )

    from_date = models.DateTimeField(
        verbose_name=_('VN__DATE_FROM'),
        help_text=_('HT__DATE_FROM')
    )

    to_date = models.DateTimeField(
        verbose_name=_('VN__DATE_TO'),
        help_text=_('HT__DATE_TO')
    )

    reason = models.CharField(
        choices=WORK_BREAK_REASONS,
        blank=False,
        max_length=15,
        verbose_name=_('VN__REASON'),
        help_text=_('HT__REASON')
    )

    comment = models.TextField(
        verbose_name=_('VN__COMMENT'),
        help_text=_('HT__COMMENT')
    )

    objects = WorkBreakManager()

    class Meta:
        verbose_name = _('VN__WORKBREAK')
        verbose_name_plural = _('VN__WORKBREAKS')
        ordering = ('-from_date',)

    def __str__(self):
        return f'{self.user}: {self.reason} ({self.from_date} - {self.to_date})'