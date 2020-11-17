from django.contrib import admin

from apps.core.admin.base import BaseModelAdmin
from apps.development.models import ProjectMember


@admin.register(ProjectMember)
class ProjectMemberAdmin(BaseModelAdmin):
    """A class represents Project Member model for admin dashboard."""

    list_display = ("id", "content_type", "owner", "user", "role")
    list_filter = ("role",)
    search_fields = ("user__login", "user__email", "role")
