from django.db import models
from django.utils.translation import gettext_lazy as _


class Label(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name=_('VN__TITLE'),
        help_text=_('HT__TITLE'),
    )

    color = models.CharField(
        max_length=10,
        verbose_name=_('VN__COLOR'),
        help_text=_('HT__COLOR'),
    )

    class Meta:
        verbose_name = _('VN__LABEL')
        verbose_name_plural = _('VN__LABELS')

    def __str__(self):
        return self.title
