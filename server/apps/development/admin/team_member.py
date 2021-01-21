from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.development.admin.forms import TeamMemberForm
from apps.development.models import TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(BaseModelAdmin):
    """A class represents Project Group model for admin dashboard."""

    list_display = ("team", "user")
    search_fields = ("team", "user__login", "user__email")
    list_filter = ("team", "user")
    form = TeamMemberForm
