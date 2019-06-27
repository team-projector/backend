from django.db import models
from django.utils.translation import gettext_lazy as _


class GitlabInternalIdMixin(models.Model):
    gl_iid = models.PositiveIntegerField(
        null=True,
        verbose_name=_('VN__GITLAB_INTERNAL_ID'),
        help_text=_('HT__GITLAB_INTERNAL_ID')
    )

    class Meta:
        abstract = True