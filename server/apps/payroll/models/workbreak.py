from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.utils import Choices
from apps.payroll.db.mixins import ApprovedMixin
from apps.users.models import User


class WorkBreak(ApprovedMixin):
    WORK_BREAK_REASONS = Choices(
        ('dayoff', _('CH_DAYOFF')),
        ('vacation', _('CH_VACATION')),
        ('disease', _('CH_DISEASES')),
    )

    user = models.ForeignKey(
        User,
        models.CASCADE,
        related_name='work_break',
        verbose_name=_('VN__USER'),
        help_text=_('HT__USER')
    )

    date_from = models.DateField(
        verbose_name=_('VN__DATE_FROM'),
        help_text=_('HT__DATE_FROM')
    )

    date_to = models.DateField(
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

    class Meta:
        verbose_name = _('VN__WORKBREAK')
        verbose_name_plural = _('VN__WORKBREAKS')
        ordering = ('-date_from',)

    def __str__(self):
        return f'{self.user} : {self.reason}'
