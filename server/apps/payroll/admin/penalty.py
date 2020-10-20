from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.payroll.models import Penalty
from apps.users.admin.filters import UserFilter


@admin.register(Penalty)
class PenaltyAdmin(BaseModelAdmin):
    """A class represents Penalty model for admin dashboard."""

    list_display = ("user", "created_by", "created_at", "sum")
    list_filter = (UserFilter,)
    search_fields = ("user__login", "user__email")
