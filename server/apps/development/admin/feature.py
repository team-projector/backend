from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from ..models import Feature


@admin.register(Feature)
class FeatureAdmin(BaseModelAdmin):
    list_display = ('id', 'title', 'start_date', 'due_date', 'budget')
    search_fields = ('title',)
