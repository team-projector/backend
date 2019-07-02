from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.mixins import Timestamps
from apps.core.db.utils import Choices
from apps.payroll.db.managers import WorkBreakManager
from apps.payroll.db.mixins import ApprovedMixin
from apps.users.models import User

DAYOFF = 'dayoff'
VACATION = 'vacation'
DISEASE = 'disease'


class WorkBreak(ApprovedMixin, Timestamps):
    WORK_BREAK_REASONS = Choices(
        (DAYOFF, _('CH_DAYOFF')),
        (VACATION, _('CH_VACATION')),
        (DISEASE, _('CH_DISEASES')),
    )

    user = models.ForeignKey(
        User,
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
