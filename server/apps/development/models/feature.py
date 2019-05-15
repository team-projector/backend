from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.mixins import Timestamps
from .milestone import Milestone


class Feature(Timestamps):
    title = models.CharField(
        max_length=255,
        verbose_name=_('VN__TITLE'),
        help_text=_('HT__TITLE')
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('VN__DESCRIPTION'),
        help_text=_('HT__DESCRIPTION')
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('VN__START_DATE'),
        help_text=_('HT__START_DATE')
    )

    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('VN__DUE_DATE'),
        help_text=_('HT__DUE_DATE')
    )

    budget = models.DecimalField(
        default=0,
        max_digits=12,
        decimal_places=2,
        verbose_name=_('VN__BUDGET'),
        help_text=_('HT__BUDGET')
    )

    milestone = models.ForeignKey(
        Milestone,
        models.CASCADE,
        related_name='feature'
    )

    class Meta:
        verbose_name = _('VN__FEATURE')
        verbose_name_plural = _('VN__FEATURES')
        ordering = ('-created_at',)
