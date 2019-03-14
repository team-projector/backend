from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.db.fields import MoneyField
from apps.core.db.mixins import Timestamps
from apps.development.models import Note

User = get_user_model()


class SpentTime(models.Model):
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    date = models.DateField(null=True)

    rate = models.FloatField(null=True, verbose_name=_('VN__RATE'), help_text=_('HT__RATE'))
    time_spent = models.IntegerField(verbose_name=_('VN__TIME_SPENT'), help_text=_('HT__TIME_SPENT'))

    user = models.ForeignKey(User, models.CASCADE, verbose_name=_('VN__USER'), help_text=_('HT__USER'))

    content_type = models.ForeignKey(ContentType, models.CASCADE)
    object_id = models.PositiveIntegerField()
    base = GenericForeignKey()

    note = models.OneToOneField(Note, models.SET_NULL, null=True, blank=True, related_name='time_spend')

    earnings = models.DecimalField(default=0, decimal_places=2, max_digits=10)

    def __str__(self):
        return f'{self.user} [{self.base}]: {self.time_spent}'

    class Meta:
        verbose_name = _('VN__SPENT_TIME')
        verbose_name_plural = _('VN__SPENT_TIMES')
        ordering = ('-date',)


class Payroll(Timestamps):
    created_by = models.ForeignKey(User, models.CASCADE, verbose_name=_('VN__CREATED_BY'),
                                   help_text=_('HT__CREATED_BY'))
    sum = MoneyField(verbose_name=_('VN__SUM'), help_text=_('HT__SUM'))
    salary = models.ForeignKey('Salary', models.SET_NULL, null=True, blank=True, related_name='+',
                               verbose_name=_('VN__SALARY'), help_text=_('HT__SALARY'))

    user = models.ForeignKey(User, models.CASCADE, related_name='+', verbose_name=_('VN__USER'),
                             help_text=_('HT__USER'))

    def __str__(self):
        return f'{self.user} [{self.created_at}]: {self.sum}'

    class Meta:
        verbose_name = _('VN__PAYROLL')
        verbose_name_plural = _('VN__PAYROLLS')
        ordering = ('-created_at',)


class Bonus(Payroll):
    description = models.TextField(verbose_name=_('VN__DESCRIPTION'), help_text=_('HT__DESCRIPTION'))

    class Meta:
        verbose_name = _('VN__BONUS')
        verbose_name_plural = _('VN__BONUSES')
        ordering = ('-created_at',)


class Penalty(Payroll):
    description = models.TextField(verbose_name=_('VN__DESCRIPTION'), help_text=_('HT__DESCRIPTION'))

    class Meta:
        verbose_name = _('VN__PENALTY')
        verbose_name_plural = _('VN__PENALTIES')
        ordering = ('-created_at',)


class Payment(Payroll):
    class Meta:
        verbose_name = _('VN__PAYMENT')
        verbose_name_plural = _('VN__PAYMENTS')
        ordering = ('-created_at',)


class Salary(Timestamps):
    created_by = models.ForeignKey(User, models.CASCADE, verbose_name=_('VN__CREATED_BY'),
                                   help_text=_('HT__CREATED_BY'))
    user = models.ForeignKey(User, models.CASCADE, related_name='salaries',
                             verbose_name=_('VN__USER'), help_text=_('HT__USER'))

    period_from = models.DateField(null=True, blank=True, verbose_name=_('VN__PERIOD_FROM'),
                                   help_text=_('HT__PERIOD_FROM'))
    period_to = models.DateField(null=True, blank=True, verbose_name=_('VN__PERIOD_TO'),
                                 help_text=_('HT__PERIOD_TO'))

    charged_time = models.IntegerField(verbose_name=_('VN__CHARGED_TIME'), help_text=_('HT__CHARGED_TIME'))

    taxes = MoneyField(verbose_name=_('VN__TAXES'), help_text=_('HT__TAXES'))
    bonus = MoneyField(verbose_name=_('VN__BONUS'), help_text=_('HT__BONUS'))
    sum = MoneyField(verbose_name=_('VN__SUM'), help_text=_('HT__SUM'))
    total = MoneyField(verbose_name=_('VN__TOTAL'), help_text=_('HT__TOTAL'))

    payed = models.BooleanField(default=False, verbose_name=_('VN__PAYED'), help_text=_('HT__PAYED'))

    def __str__(self):
        return f'{self.user} [{self.created_at}]: {self.sum}'

    class Meta:
        verbose_name = _('VN__SALARY')
        verbose_name_plural = _('VN__SALARIES')
        ordering = ('-created_at',)
