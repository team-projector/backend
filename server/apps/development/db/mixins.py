from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notable(models.Model):
    notes = GenericRelation('development.Note', verbose_name=_('VN__NOTES'), help_text=_('HT__NOTES'))

    class Meta:
        abstract = True