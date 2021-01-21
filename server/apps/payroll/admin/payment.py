from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.payroll.models import Payment


@admin.register(Payment)
class PaymentAdmin(BaseModelAdmin):
    """A class represents Payment model for admin dashboard."""

    list_display = ("user", "created_by", "created_at", "sum")
    list_filter = ("user",)
    search_fields = ("user__login", "user__email")
