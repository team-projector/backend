# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.consts import DEFAULT_TITLE_LENGTH
from apps.core.models.mixins import Timestamps
from apps.core.models.utils import Choices

TYPE_FEATURE = 'FEATURE'
TYPE_IMPROVEMENT = 'IMPROVEMENT'
TYPE_BUG_FIXING = 'BUG_FIXING'

TICKET_TYPES = Choices(
    (TYPE_FEATURE, _('CH_FEATURE')),
    (TYPE_IMPROVEMENT, _('CH_IMPROVEMENT')),
    (TYPE_BUG_FIXING, _('CH_BUG_FIXING')),
)

TICKET_TYPE_MAX_LENGTH = 50
TICKET_ROLE_MAX_LENGTH = 50


class Ticket(Timestamps):
    """The ticket model."""

    type = models.CharField(  # noqa: A003
        choices=TICKET_TYPES,
        max_length=TICKET_TYPE_MAX_LENGTH,
        blank=True,
        verbose_name=_('VN__TYPE'),
        help_text=_('HT__TYPE'),
    )

    title = models.CharField(
        max_length=DEFAULT_TITLE_LENGTH,
        verbose_name=_('VN__TITLE'),
        help_text=_('HT__TITLE'),
    )

    start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('VN__START_DATE'),
        help_text=_('HT__START_DATE'),
    )

    due_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('VN__DUE_DATE'),
        help_text=_('HT__DUE_DATE'),
    )

    url = models.URLField(
        blank=True,
        verbose_name=_('VN__URL'),
        help_text=_('HT__URL'),
    )

    milestone = models.ForeignKey(
        'development.Milestone',
        models.CASCADE,
        related_name='ticket',
        blank=True,
        null=True,
        verbose_name=_('VN__MILESTONE'),
    )

    role = models.CharField(
        max_length=TICKET_ROLE_MAX_LENGTH,
        blank=True,
        verbose_name=_('VN__ROLE'),
        help_text=_('HT__ROLE'),
    )

    class Meta:
        verbose_name = _('VN__TICKET')
        verbose_name_plural = _('VN__TICKETS')
        ordering = ('-created_at',)
