from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.users.admin.filters import UserFilter
from ..models import Bonus, Payment, Payroll, Penalty, Salary, SpentTime


@admin.register(Salary)
class SalaryAdmin(BaseModelAdmin):
    list_display = ('user', 'created_by', 'created_at', 'total', 'payed')
    list_filter = (UserFilter,)
    search_fields = ('user',)
    autocomplete_fields = ('user', 'created_by')


@admin.register(Payroll)
class PayrollAdmin(BaseModelAdmin):
    list_display = ('user', 'created_by', 'created_at', 'sum')
    list_filter = (UserFilter,)
    search_fields = ('user',)
    autocomplete_fields = ('user', 'created_by', 'salary')


@admin.register(SpentTime)
class SpentTimeAdmin(BaseModelAdmin):
    list_display = ('user', 'created_at', 'date', 'content_type', 'object_id', 'time_spent')
    search_fields = ('user',)
    autocomplete_fields = ('note', 'user', 'created_by')


@admin.register(Bonus)
class BonusAdmin(BaseModelAdmin):
    list_display = ('user', 'created_by', 'created_at', 'sum')
    list_filter = (UserFilter,)
    search_fields = ('user',)
    autocomplete_fields = ('user', 'created_by', 'salary')


@admin.register(Penalty)
class PenaltyAdmin(BaseModelAdmin):
    list_display = ('user', 'created_by', 'created_at', 'sum')
    list_filter = (UserFilter,)
    search_fields = ('user',)
    autocomplete_fields = ('user', 'created_by', 'salary')


@admin.register(Payment)
class PaymentAdmin(BaseModelAdmin):
    list_display = ('user', 'created_by', 'created_at', 'sum')
    list_filter = (UserFilter,)
    search_fields = ('user',)
    autocomplete_fields = ('user', 'created_by', 'salary')
