from django.db import models
from django.utils.translation import gettext_lazy as _


class GitlabInternalIdMixin(models.Model):
    """A mixin for Gitlab entity."""

    class Meta:
        abstract = True

    gl_iid = models.PositiveIntegerField(
        null=True,
        verbose_name=_("VN__GITLAB_INTERNAL_ID"),
        help_text=_("HT__GITLAB_INTERNAL_ID"),
    )

    def __str__(self):
        """Returns object string representation."""
        return str(self.gl_iid)
