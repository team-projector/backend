from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.fields import MoneyField
from apps.core.db.mixins import Timestamps

User = get_user_model()


class Payroll(Timestamps):
    created_by = models.ForeignKey(User, models.CASCADE, verbose_name=_('VN__CREATED_BY'),
                                   help_text=_('HT__CREATED_BY'))
    sum = MoneyField(default=0, verbose_name=_('VN__SUM'), help_text=_('HT__SUM'))
    salary = models.ForeignKey('Salary', models.SET_NULL, null=True, blank=True, related_name='payrolls',
                               verbose_name=_('VN__SALARY'), help_text=_('HT__SALARY'))

    user = models.ForeignKey(User, models.CASCADE, related_name='+', verbose_name=_('VN__USER'),
                             help_text=_('HT__USER'))

    def __str__(self):
        return f'{self.user} [{self.created_at}]: {self.sum}'

    class Meta:
        verbose_name = _('VN__PAYROLL')
        verbose_name_plural = _('VN__PAYROLLS')
        ordering = ('-created_at',)
