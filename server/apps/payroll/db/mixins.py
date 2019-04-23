from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.utils import Choices
from apps.users.models import User


class SpentTimesMixin(models.Model):
    time_spents = GenericRelation(
        'payroll.SpentTime',
        related_query_name='%(class)ss',
        verbose_name=_('VN__TIME_SPENTS'),
        help_text=_('HT__TIME_SPENTS')
    )

    class Meta:
        abstract = True


class ApprovedMixin(models.Model):
    APPROVED_STATES = Choices(
        ('created', _('CH_CREATED')),
        ('approved', _('CH_APPROVED')),
        ('declined', _('CH_DECLINED')),
    )

    approve_state = models.CharField(
        choices=APPROVED_STATES,
        default='created',
        max_length=15,
        verbose_name=_('VN__APPROVE_STATE'),
        help_text=_('HT__APPROVE_STATE')
    )

    approved_at = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('VN__APPROVED_AT'),
        help_text=_('HT__APPROVED_AT')
    )

    approved_by = models.ForeignKey(
        User,
        models.SET_NULL,
        related_name='approve_break',
        null=True,
        blank=True,
        verbose_name=_('VN__APPROVED_BY'),
        help_text=_('HT__APPROVED_BY')
    )

    decline_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('VN__DECLINE_REASON'),
        help_text=_('HT__DECLINE_REASON')
    )

    class Meta:
        abstract = True
