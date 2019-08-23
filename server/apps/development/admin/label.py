from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from ..models import Label


@admin.register(Label)
class LabelAdmin(BaseModelAdmin):
    list_display = ('title', 'color')
    search_fields = ('title',)
