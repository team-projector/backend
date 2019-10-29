# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.admin import helpers
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import path, reverse

from apps.core.admin.base import BaseModelAdmin
from apps.payroll.admin.forms import GenerateSalaryForm
from apps.payroll.models import Salary
from apps.payroll.services.salary.calculator import SalaryCalculator
from apps.payroll.services.salary.notifications import is_payed
from apps.payroll.tasks import send_salary_report_task
from apps.users.admin.filters import UserFilter


@admin.register(Salary)
class SalaryAdmin(BaseModelAdmin):
    """A class representing Salary model for admin dashboard."""

    list_display = ('user', 'created_by', 'created_at', 'total', 'payed')
    list_filter = (UserFilter,)
    search_fields = ('user__login', 'user__email')

    def get_urls(self):
        """Add url for generate salaries form."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'generate/',
                self.admin_site.admin_view(self.generate_salaries),
                name='generate-salaries',
            ),
        ]
        return custom_urls + urls

    def generate_salaries(self, request):
        """Generate salaries."""
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

    def save_model(self, request, salary, form, change):
        """
        Save salary.

        Send notification to user if salary is payed.
        """
        if change and is_payed(salary):
            transaction.on_commit(
                lambda: send_salary_report_task.delay(salary.id),
            )

        super().save_model(request, salary, form, change)
