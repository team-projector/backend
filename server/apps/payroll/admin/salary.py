# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.admin import helpers
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import path, reverse

from apps.core.admin.base import BaseModelAdmin
from apps.payroll.admin.forms import GenerateSalaryForm
from apps.payroll.services.salary.calculator import SalaryCalculator
from apps.payroll.services.salary.notifications import is_payed
from apps.payroll.tasks import send_salary_report
from apps.users.admin.filters import UserFilter

from ..models import Salary


@admin.register(Salary)
class SalaryAdmin(BaseModelAdmin):
    list_display = ('user', 'created_by', 'created_at', 'total', 'payed')
    list_filter = (UserFilter,)
    search_fields = ('user__login', 'user__email')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate/',
                 self.admin_site.admin_view(self.generate_salaries),
                 name='generate-salaries',
                 ),
        ]
        return custom_urls + urls

    def generate_salaries(self, request):
        if request.method == 'POST':
            form = GenerateSalaryForm(request.POST)
            if form.is_valid():
                calculator = SalaryCalculator(
                    request.user,
                    form.cleaned_data['period_from'],
                    form.cleaned_data['period_to'],
                )
                calculator.generate_bulk()

                return redirect(reverse('admin:payroll_salary_changelist'))
        else:
            form = GenerateSalaryForm()

        context = self.admin_site.each_context(request)
        context['title'] = 'Generate salaries'
        context['form'] = form
        context['adminform'] = helpers.AdminForm(
            form,
            [(None, {'fields': form.base_fields})],
            self.get_prepopulated_fields(request),
        )

        return render(
            request,
            'admin/payrolls/forms/generate_salaries.html',
            context,
        )

    def save_model(self, request, obj, form, change):
        if change and is_payed(obj):
            transaction.on_commit(lambda: send_salary_report.delay(obj.id))

        super().save_model(request, obj, form, change)
