from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from jnt_admin_tools.db.fields import GenericForeignKey
from jnt_django_toolbox.models.fields import EnumField

from apps.core.consts import DEFAULT_MAX_DIGITS, DEFAULT_TITLE_LENGTH
from apps.core.models.mixins import (
    GitlabEntityMixin,
    GitlabInternalIdMixin,
    Timestamps,
)

MILESTONE_STATE_MAX_LENGTH = 20


class MilestoneState(models.TextChoices):
    """Milestone state choices."""

    ACTIVE = "ACTIVE", _("CH__STATE_ACTIVE")  # noqa: WPS115
    CLOSED = "CLOSED", _("CH__STATE_CLOSED")  # noqa: WPS115


class Milestone(
    GitlabEntityMixin,
    GitlabInternalIdMixin,
    Timestamps,
):
    """The milestone model."""

    class Meta:
        verbose_name = _("VN__MILESTONE")
        verbose_name_plural = _("VN__MILESTONES")
        ordering = ("-created_at",)

    title = models.CharField(
        max_length=DEFAULT_TITLE_LENGTH,
        verbose_name=_("VN__TITLE"),
        help_text=_("HT__TITLE"),
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("VN__DESCRIPTION"),
        help_text=_("HT__DESCRIPTION"),
    )

    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("VN__START_DATE"),
        help_text=_("HT__START_DATE"),
    )

    state = EnumField(
        enum=MilestoneState,
        blank=True,
        verbose_name=_("VN__STATE"),
        help_text=_("HT__STATE"),
    )

    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("VN__DUE_DATE"),
        help_text=_("HT__DUE_DATE"),
    )

    budget = models.DecimalField(
        default=0,
        max_digits=DEFAULT_MAX_DIGITS,
        decimal_places=2,
        verbose_name=_("VN__BUDGET"),
        help_text=_("HT__BUDGET"),
    )

    object_id = models.PositiveIntegerField()

    owner = GenericForeignKey()
    content_type = models.ForeignKey(  # noqa: CCE001
        ContentType,
        models.CASCADE,
    )

    def __str__(self):
        """Returns object string representation."""
        return "{0} / {1}".format(self.owner.title, self.title)
