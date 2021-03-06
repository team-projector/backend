from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.payroll.models import Penalty


@admin.register(Penalty)
class PenaltyAdmin(BaseModelAdmin):
    """A class represents Penalty model for admin dashboard."""

    list_display = ("user", "created_by", "created_at", "sum")
    list_filter = ("user",)
    search_fields = ("user__login", "user__email")
