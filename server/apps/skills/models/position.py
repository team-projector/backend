from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.consts import DEFAULT_TITLE_LENGTH


class Position(models.Model):
    """The Position model."""

    class Meta:
        verbose_name = _("VN__POSITION")
        verbose_name_plural = _("VN__POSITIONS")
        ordering = ("title",)

    title = models.CharField(
        max_length=DEFAULT_TITLE_LENGTH,
        unique=True,
        verbose_name=_("VN__TITLE"),
        help_text=_("HT__TITLE"),
    )

    def __str__(self):
        """Returns object string representation."""
        return self.title
