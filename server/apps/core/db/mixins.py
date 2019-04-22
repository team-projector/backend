from django.db import models
from django.utils.translation import gettext_lazy as _


class GitlabEntityMixin(models.Model):
    gl_id = models.PositiveIntegerField(
        unique=True,
        verbose_name=_('VN__GITLAB_ID'),
        help_text=_('HT__GITLAB_ID')
    )
    gl_url = models.URLField(
        unique=True,
        verbose_name=_('VN__GITLAB_URL'),
        help_text=_('HT__GITLAB_URL')
    )
    gl_last_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('VN__GITLAB_LAST_SYNC'),
        help_text=_('HT__GITLAB_LAST_SYNC')
    )

    class Meta:
        abstract = True


class GitlabInternalIdMixin(models.Model):
    gl_iid = models.PositiveIntegerField(
        null=True,
        verbose_name=_('VN__GITLAB_INTERNAL_ID'),
        help_text=_('HT__GITLAB_INTERNAL_ID')
    )

    class Meta:
        abstract = True


class Timestamps(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
