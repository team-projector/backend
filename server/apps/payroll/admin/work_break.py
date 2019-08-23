from django.contrib import admin
from django.contrib.admin import helpers
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models.fields.related import OneToOneRel
from django.shortcuts import redirect, render
from django.utils.html import mark_safe
from django.urls import path, reverse

from apps.core.admin.base import BaseModelAdmin
from apps.payroll.admin.forms import GenerateSalaryForm
from apps.payroll.services.salary.calculator import SalaryCalculator
from apps.payroll.services.salary.notifications import is_payed
from apps.payroll.tasks import send_salary_report
from apps.users.admin.filters import UserFilter
from .filters import HasSalaryFilter
from ..models import (
    Bonus, Payment, Payroll, Penalty, Salary, SpentTime, WorkBreak
)





@admin.register(WorkBreak)
class WorkBreakAdmin(BaseModelAdmin):
    list_display = ('user', 'reason', 'from_date', 'to_date', 'approve_state')
    list_filter = (UserFilter,)
    search_fields = ('user__login', 'user__email')
    fieldsets = (
        (None, {
            'fields': ('user', 'reason', 'from_date', 'to_date', 'comment')
        }),
        ('Approve status', {
            'fields': (
                'approve_state', 'approved_at', 'approved_by', 'decline_reason')
        })
    )
