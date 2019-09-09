from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.mixins import Timestamps
from apps.core.models.utils import Choices

TYPE_FEATURE = 'feature'
TYPE_IMPROVEMENT = 'improvement'
TYPE_BUG_FIXING = 'bug_fixing'


class Ticket(Timestamps):
    TYPE = Choices(
        (TYPE_FEATURE, _('CH_FEATURE')),
        (TYPE_IMPROVEMENT, _('CH_IMPROVEMENT')),
        (TYPE_BUG_FIXING, _('CH_BUG_FIXING')),
    )

    type = models.CharField(
        choices=TYPE,
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('VN__TYPE'),
        help_text=_('HT__TYPE')
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_('VN__TITLE'),
        help_text=_('HT__TITLE')
    )

    start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('VN__START_DATE'),
        help_text=_('HT__START_DATE')
    )

    due_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('VN__DUE_DATE'),
        help_text=_('HT__DUE_DATE')
    )

    url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('VN__URL'),
        help_text=_('HT__URL')
    )

    milestone = models.ForeignKey(
        'development.Milestone',
        models.CASCADE,
        related_name='ticket',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('VN__TICKET')
        verbose_name_plural = _('VN__TICKETS')
        ordering = ('-created_at',)