from django.db import models
from django.utils.translation import gettext_lazy as _


class GitlabEntityMixin(models.Model):
    gitlab_id = models.PositiveIntegerField(verbose_name=_('VN__GITLAB_ID'), help_text=_('HT__GITLAB_ID'))
    gitlab_url = models.URLField(verbose_name=_('VN__GITLAB_URL'), help_text=_('HT__GITLAB_URL'))
    gitlab_last_sync = models.DateTimeField(null=True, blank=True, verbose_name=_('VN__GITLAB_LAST_SYNC'),
                                            help_text=_('HT__GITLAB_LAST_SYNC'))

    class Meta:
        abstract = True
