from django.db import models
from django.utils.translation import gettext_lazy as _


class Team(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name=_('VN__TITLE'),
        help_text=_('HT__TITLE'),
        unique=True
    )

    class Meta:
        verbose_name = _('VN__TEAM')
        verbose_name_plural = _('VN__TEAMS')
        ordering = ('title',)

    def __str__(self):
        return self.title
