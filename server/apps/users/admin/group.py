from django.contrib import admin
from django.contrib.auth.models import Group

from apps.core.admin.base import BaseModelAdmin
from apps.users.admin.forms import GroupAdminForm

admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseModelAdmin):
    """A class represents Group model for admin dashboard."""

    form = GroupAdminForm
    list_display = ("name",)
    search_fields = ("name",)
