from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from jnt_django_toolbox.models.fields import EnumField

from apps.core.consts import DEFAULT_TITLE_LENGTH
from apps.core.models.mixins import Timestamps

TICKET_TYPE_MAX_LENGTH = 50
TICKET_ROLE_MAX_LENGTH = 50
TICKET_STATE_MAX_LENGTH = 50


class TicketType(models.TextChoices):
    """Ticket types choices."""

    FEATURE = "FEATURE", _("CH__FEATURE")  # noqa: WPS115
    IMPROVEMENT = "IMPROVEMENT", _("CH__IMPROVEMENT")  # noqa: WPS115
    BUG_FIXING = "BUG_FIXING", _("CH__BUG_FIXING")  # noqa: WPS115


class TicketState(models.TextChoices):
    """Ticket states choices."""

    CREATED = "CREATED", _("CH__CREATED")  # noqa: WPS115
    PLANNING = "PLANNING", _("CH__PLANNING")  # noqa: WPS115
    DOING = "DOING", _("CH__DOING")  # noqa: WPS115
    TESTING = "TESTING", _("CH__TESTING")  # noqa: WPS115
    ACCEPTING = "ACCEPTING", _("CH__ACCEPTING")  # noqa: WPS115
    DONE = "DONE", _("CH__DONE")  # noqa: WPS115


class Ticket(Timestamps):
    """The ticket model."""

    class Meta:
        verbose_name = _("VN__TICKET")
        verbose_name_plural = _("VN__TICKETS")
        ordering = ("-created_at",)

    type = EnumField(  # noqa: WPS125, A003
        enum=TicketType,
        default=TicketType.FEATURE,
        blank=True,
        verbose_name=_("VN__TYPE"),
        help_text=_("HT__TYPE"),
    )

    title = models.CharField(
        max_length=DEFAULT_TITLE_LENGTH,
        verbose_name=_("VN__TITLE"),
        help_text=_("HT__TITLE"),
    )

    start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("VN__START_DATE"),
        help_text=_("HT__START_DATE"),
    )

    due_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_("VN__DUE_DATE"),
        help_text=_("HT__DUE_DATE"),
    )

    url = models.URLField(
        blank=True,
        verbose_name=_("VN__URL"),
        help_text=_("HT__URL"),
    )

    role = models.CharField(
        max_length=TICKET_ROLE_MAX_LENGTH,
        blank=True,
        verbose_name=_("VN__ROLE"),
        help_text=_("HT__ROLE"),
    )

    estimate = models.PositiveIntegerField(
        default=0,
        verbose_name=_("VN__ESTIMATE"),
        help_text=_("HT__ESTIMATE"),
    )

    state = EnumField(
        enum=TicketState,
        default=TicketState.CREATED,
        blank=True,
        verbose_name=_("VN__STATE"),
        help_text=_("HT__STATE"),
    )

    milestone = models.ForeignKey(
        "development.Milestone",
        models.CASCADE,
        related_name="ticket",
        blank=True,
        null=True,
        verbose_name=_("VN__MILESTONE"),
    )

    def __str__(self):
        """String representation."""
        return self.title

    @property
    def site_url(self):
        """Get ticket url on main site."""
        return "https://{0}/tickets/{1}".format(settings.DOMAIN_NAME, self.pk)
