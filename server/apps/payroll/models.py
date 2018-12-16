from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.mixins import Timestamps
from apps.users.models import User


class TimeSpend(Timestamps):
    time_spent = models.IntegerField(verbose_name=_('VN__TIME_SPENT'),
                                     help_text=_('HT__TIME_SPENT'))

    employee = models.ForeignKey(User, models.CASCADE, verbose_name=_('VN__EMPLOYEE'),
                                 help_text=_('HT__EMPLOYEE'))

    content_type = models.ForeignKey(ContentType, models.CASCADE)
    object_id = models.PositiveIntegerField()
    reason = GenericForeignKey()

    salary = models.DecimalField(default=0, decimal_places=2, max_digits=10)

    def __str__(self):
        return f'{self.employee} [{self.reason}]: {self.time_spent}'

    class Meta:
        verbose_name = _('VN__TIME_SPEND')
        verbose_name_plural = _('VN__TIME_SPEND')
        ordering = ('-created_at', 'employee')
