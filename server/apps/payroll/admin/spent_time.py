# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.users.admin.filters import UserFilter

from ..models import SpentTime


@admin.register(SpentTime)
class SpentTimeAdmin(BaseModelAdmin):
    list_display = (
        'user', 'created_at', 'date', 'content_type', 'object_id', 'time_spent',
    )
    search_fields = ('user__login', 'user__email')
    list_filter = (UserFilter,)
