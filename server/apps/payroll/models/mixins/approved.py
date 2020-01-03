# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.utils import Choices
from apps.users.models import User

APPROVED_STATES = Choices(
    ("CREATED", _("CH_CREATED")),
    ("APPROVED", _("CH_APPROVED")),
    ("DECLINED", _("CH_DECLINED")),
)

APPROVED_STATE_MAX_LENGTH = 15


class ApprovedMixin(models.Model):
    """A mixin for approving or decline work break."""

    approve_state = models.CharField(
        choices=APPROVED_STATES,
        default=APPROVED_STATES.CREATED,
        max_length=APPROVED_STATE_MAX_LENGTH,
        verbose_name=_("VN__APPROVE_STATE"),
        help_text=_("HT__APPROVE_STATE"),
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("VN__APPROVED_AT"),
        help_text=_("HT__APPROVED_AT"),
    )

    approved_by = models.ForeignKey(
        User,
        models.SET_NULL,
        related_name="approve_break",
        null=True,
        blank=True,
        verbose_name=_("VN__APPROVED_BY"),
        help_text=_("HT__APPROVED_BY"),
    )

    decline_reason = models.TextField(
        blank=True,
        verbose_name=_("VN__DECLINE_REASON"),
        help_text=_("HT__DECLINE_REASON"),
    )

    class Meta:
        abstract = True

    def __str__(self):
        """Returns object string representation."""
        return self.approve_state
