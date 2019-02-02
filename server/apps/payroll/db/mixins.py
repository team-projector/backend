from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _


class SpentTimesMixin(models.Model):
    time_spents = GenericRelation('payroll.SpentTime', verbose_name=_('VN__TIME_SPENTS'),
                                  help_text=_('HT__TIME_SPENTS'))

    class Meta:
        abstract = True
