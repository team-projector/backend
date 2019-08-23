from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from .inlines import TeamMemberInline
from ..models import Team


@admin.register(Team)
class TeamAdmin(BaseModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    inlines = (TeamMemberInline,)
