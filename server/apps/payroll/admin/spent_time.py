# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.payroll.models import SpentTime
from apps.users.admin.filters import UserFilter


@admin.register(SpentTime)
class SpentTimeAdmin(BaseModelAdmin):
    """A class representing Spent Time model for admin dashboard."""

    list_display = (
        "user",
        "created_at",
        "date",
        "content_type",
        "object_id",
        "time_spent",
    )
    search_fields = ("user__login", "user__email")
    list_filter = (UserFilter,)
