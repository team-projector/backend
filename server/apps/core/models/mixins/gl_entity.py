from django.db import models
from django.utils.translation import gettext_lazy as _


class GitlabEntityMixin(models.Model):
    """A mixin for Gitlab entity."""

    class Meta:
        abstract = True

    gl_id = models.PositiveIntegerField(
        unique=True,
        blank=True,
        verbose_name=_("VN__GITLAB_ID"),
        help_text=_("HT__GITLAB_ID"),
    )

    gl_url = models.URLField(
        blank=True,
        verbose_name=_("VN__GITLAB_URL"),
        help_text=_("HT__GITLAB_URL"),
    )

    gl_last_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("VN__GITLAB_LAST_SYNC"),
        help_text=_("HT__GITLAB_LAST_SYNC"),
    )

    def __str__(self):
        """Returns object string representation."""
        return str(self.gl_id)
