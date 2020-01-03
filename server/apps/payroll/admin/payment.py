# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.payroll.models import Payment
from apps.users.admin.filters import UserFilter


@admin.register(Payment)
class PaymentAdmin(BaseModelAdmin):
    """A class representing Payment model for admin dashboard."""

    list_display = ("user", "created_by", "created_at", "sum")
    list_filter = (UserFilter,)
    search_fields = ("user__login", "user__email")
