from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import Group
from django.utils.html import format_html

from apps.core.admin.base import BaseModelAdmin
from .forms import GroupAdminForm
from .models import User

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(UserAdmin):
    model = User
    list_display = (
        'login', 'last_login', 'is_active', 'is_staff', 'change_password_link'
    )
    list_filter = ('is_active', 'is_staff', 'is_active')
    ordering = ('login',)
    sortable_by = ()
    fieldsets = ()
    autocomplete_fields = ('groups',)
    search_fields = ('login',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'password1', 'password2')}
         ),
    )

    exclude = ('user_permissions',)
    fields = (
        'login', 'groups', 'is_superuser', 'is_staff', 'is_active', 'last_login'
    )
    readonly_fields = ('last_login',)

    def change_password_link(self, obj):
        return format_html(f'<a href="{obj.id}/password/">change password</a>')

    change_password_link.short_description = 'Change password link'
    change_password_link.allow_tags = True

    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseModelAdmin):
    list_display = ('name',)
    form = GroupAdminForm
    search_fields = ('name',)
