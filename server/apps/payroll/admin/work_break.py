from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.payroll.models import WorkBreak


@admin.register(WorkBreak)
class WorkBreakAdmin(BaseModelAdmin):
    """A class represents Work Break model for admin dashboard."""

    list_display = (
        "user",
        "reason",
        "from_date",
        "to_date",
        "approve_state",
        "paid_days",
    )
    list_filter = ("user",)
    search_fields = ("user__login", "user__email")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user",
                    "reason",
                    "from_date",
                    "to_date",
                    "comment",
                    "paid_days",
                    "paid",
                ),
            },
        ),
        (
            "Approve status",
            {
                "fields": (
                    "approve_state",
                    "approved_at",
                    "approved_by",
                    "decline_reason",
                ),
            },
        ),
    )
