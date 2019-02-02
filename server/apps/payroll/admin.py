from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from .models import SpentTime


@admin.register(SpentTime)
class SpentTimeAdmin(BaseModelAdmin):
    list_display = ('employee', 'date', 'content_type', 'object_id', 'time_spent')
    search_fields = ('employee',)
    autocomplete_fields = ('note', 'employee')
