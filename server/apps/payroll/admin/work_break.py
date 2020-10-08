from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.payroll.models import WorkBreak
from apps.users.admin.filters import UserFilter


@admin.register(WorkBreak)
class WorkBreakAdmin(BaseModelAdmin):
    """A class representing Work Break model for admin dashboard."""

    list_display = ("user", "reason", "from_date", "to_date", "approve_state")
    list_filter = (UserFilter,)
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
