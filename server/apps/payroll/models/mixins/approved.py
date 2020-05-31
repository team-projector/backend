# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.users.models import User


class ApprovedState(models.TextChoices):
    """Approved state choices."""

    CREATED = "CREATED", _("CH__CREATED")  # noqa: WPS115
    APPROVED = "APPROVED", _("CH__APPROVED")  # noqa: WPS115
    DECLINED = "DECLINED", _("CH__DECLINED")  # noqa: WPS115


APPROVED_STATE_MAX_LENGTH = 15


class ApprovedMixin(models.Model):
    """A mixin for approving or decline work break."""

    class Meta:
        abstract = True

    approve_state = models.CharField(
        choices=ApprovedState.choices,
        default=ApprovedState.CREATED,
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

    decline_reason = models.TextField(
        blank=True,
        verbose_name=_("VN__DECLINE_REASON"),
        help_text=_("HT__DECLINE_REASON"),
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

    def __str__(self):
        """Returns object string representation."""
        return self.approve_state
