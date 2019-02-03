from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.mixins import Timestamps
from apps.development.models import Note
from apps.users.models import User


class SpentTime(Timestamps):
    date = models.DateTimeField(null=True)

    time_spent = models.IntegerField(verbose_name=_('VN__TIME_SPENT'), help_text=_('HT__TIME_SPENT'))

    employee = models.ForeignKey(User, models.CASCADE, verbose_name=_('VN__EMPLOYEE'),
                                 help_text=_('HT__EMPLOYEE'))

    content_type = models.ForeignKey(ContentType, models.CASCADE)
    object_id = models.PositiveIntegerField()
    base = GenericForeignKey()

    note = models.OneToOneField(Note, models.SET_NULL, null=True, blank=True, related_name='time_spend')

    earnings = models.DecimalField(default=0, decimal_places=2, max_digits=10)

    def __str__(self):
        return f'{self.employee} [{self.base}]: {self.time_spent}'

    class Meta:
        verbose_name = _('VN__SPENT_TIME')
        verbose_name_plural = _('VN__SPENT_TIME')
        ordering = ('-date',)
