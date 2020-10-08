from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models.mixins import Timestamps
from apps.payroll.models.mixins import ApprovedMixin


class WorkBreakReason(models.TextChoices):
    """Work break reason choices."""

    DAYOFF = "DAYOFF", _("CH__DAYOFF")  # noqa: WPS115
    VACATION = "VACATION", _("CH__VACATION")  # noqa: WPS115
    DISEASE = "DISEASE", _("CH__DISEASE")  # noqa: WPS115


WORK_BREAK_REASON_MAX_LENGTH = 15


class WorkBreak(ApprovedMixin, Timestamps):
    """The work break model."""

    class Meta:
        verbose_name = _("VN__WORKBREAK")
        verbose_name_plural = _("VN__WORKBREAKS")
        ordering = ("-from_date",)

    from_date = models.DateTimeField(
        verbose_name=_("VN__DATE_FROM"),
        help_text=_("HT__DATE_FROM"),
    )

    to_date = models.DateTimeField(
        verbose_name=_("VN__DATE_TO"),
        help_text=_("HT__DATE_TO"),
    )

    reason = models.CharField(
        choices=WorkBreakReason.choices,
        blank=False,
        max_length=WORK_BREAK_REASON_MAX_LENGTH,
        verbose_name=_("VN__REASON"),
        help_text=_("HT__REASON"),
    )

    comment = models.TextField(
        verbose_name=_("VN__COMMENT"),
        help_text=_("HT__COMMENT"),
    )

    paid = models.BooleanField(
        default=False,
        verbose_name=_("VN__PAID"),
        help_text=_("HT__PAID"),
    )

    user = models.ForeignKey(  # noqa: CCE001
        settings.AUTH_USER_MODEL,
        models.CASCADE,
        related_name="work_breaks",
        verbose_name=_("VN__USER"),
        help_text=_("HT__USER"),
    )

    def __str__(self):
        """Returns object string representation."""
        return "{0}: {1} ({2} - {3})".format(
            self.user,
            self.reason,
            self.from_date,
            self.to_date,
        )
