# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.payroll.models import Bonus
from apps.users.admin.filters import UserFilter


@admin.register(Bonus)
class BonusAdmin(BaseModelAdmin):
    """A class representing Bonus model for admin dashboard."""

    list_display = ("user", "created_by", "created_at", "sum")
    list_filter = (UserFilter,)
    search_fields = ("user__login", "user__email")
