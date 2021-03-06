from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.consts import DEFAULT_TITLE_LENGTH

COLOR_MAX_LENGTH = 10
LABEL_DONE = "done"


class Label(models.Model):
    """
    The label model.

    Fill from Gitlab.
    """

    class Meta:
        verbose_name = _("VN__LABEL")
        verbose_name_plural = _("VN__LABELS")
        ordering = ("title",)

    title = models.CharField(
        max_length=DEFAULT_TITLE_LENGTH,
        verbose_name=_("VN__TITLE"),
        help_text=_("HT__TITLE"),
    )

    color = models.CharField(
        max_length=COLOR_MAX_LENGTH,
        verbose_name=_("VN__COLOR"),
        help_text=_("HT__COLOR"),
    )

    def __str__(self):
        """Returns object string representation."""
        return self.title
