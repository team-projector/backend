from django.contrib import admin
from django.contrib.admin import helpers
from django.shortcuts import redirect, render
from django.urls import path, reverse

from apps.core.admin.base import BaseModelAdmin
from apps.payroll.admin.forms import GenerateSalariesForm
from apps.payroll.utils.salary.calculator import SalaryCalculator
from apps.users.admin.filters import UserFilter
from ..models import Bonus, Payment, Payroll, Penalty, Salary, SpentTime, WorkBreak


@admin.register(Salary)
class SalaryAdmin(BaseModelAdmin):
    list_display = ('user', 'created_by', 'created_at', 'total', 'payed')
    list_filter = (UserFilter,)
    search_fields = ('user',)
    autocomplete_fields = ('user', 'created_by')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate/', self.admin_site.admin_view(self.generate_salaries), name='generate-salaries')
        ]
        return custom_urls + urls

    def generate_salaries(self, request):
        if request.method == 'POST':
            form = GenerateSalariesForm(request.POST)
            if form.is_valid():
                calculator = SalaryCalculator(request.user,
                                              form.cleaned_data['period_from'],
                                              form.cleaned_data['period_to'])
                calculator.generate_bulk()

                return redirect(reverse('admin:payroll_salary_changelist'))
        else:
            form = GenerateSalariesForm()

        context = self.admin_site.each_context(request)
        context['title'] = 'Generate salaries'
        context['form'] = form
        context['adminform'] = helpers.AdminForm(form, [(None, {'fields': form.base_fields})],
                                                 self.get_prepopulated_fields(request))

        return render(request, 'admin/payrolls/forms/generate_salaries.html', context)


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


@admin.register(WorkBreak)
class WorkBreakAdmin(BaseModelAdmin):
    list_display = ('user', 'reason', 'from_date', 'to_date', 'approve_state')
    list_filter = (UserFilter,)
    search_fields = ('user',)
    autocomplete_fields = ('user', 'approved_by')
    fieldsets = (
        (None, {
            'fields': ('user', 'reason', 'from_date', 'to_date', 'comment')
        }),
        ('Approve status', {
            'fields': ('approve_state', 'approved_at', 'approved_by', 'decline_reason')
        })
    )
