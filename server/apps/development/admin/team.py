from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.development.admin.inlines import TeamMemberInline
from apps.development.models import Team


@admin.register(Team)
class TeamAdmin(BaseModelAdmin):
    """A class represents Project Group model for admin dashboard."""

    list_display = ("title",)
    search_fields = ("title",)
    inlines = (TeamMemberInline,)
