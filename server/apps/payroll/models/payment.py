from django.utils.translation import gettext_lazy as _

from .payroll import Payroll


class Payment(Payroll):
    class Meta:
        verbose_name = _('VN__PAYMENT')
        verbose_name_plural = _('VN__PAYMENTS')
        ordering = ('-created_at',)
