# -*- coding: utf-8 -*-

from typing import Dict

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjUserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from jnt_admin_tools.decorators import admin_field

from apps.core.admin import base, mixins
from apps.development.tasks import sync_user_task
from apps.users.admin.forms import UserAdminForm
from apps.users.models import User


@admin.register(User)
class UserAdmin(
    mixins.ForceSyncEntityMixin,
    DjUserAdmin,
    base.BaseModelAdmin,
):
    """A class representing User model for admin dashboard."""

    list_display = (
        "login",
        "name",
        "email",
        "hour_rate",
        "last_login",
        "is_active",
        "is_staff",
        "change_password_link",
    )
    list_filter = ("is_active", "is_staff")
    ordering = ("login",)
    sortable_by = ()
    search_fields = ("login",)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("login", "password1", "password2"),
            },
        ),
    )

    exclude = ("user_permissions",)
    form = UserAdminForm
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "login",
                    "email",
                    "name",
                    "roles",
                    "is_superuser",
                    "is_staff",
                    "is_active",
                    "last_login",
                    "position",
                    "groups",
                ),
            },
        ),
        (
            "GitLab",
            {
                "fields": (
                    "gl_avatar",
                    "gl_id",
                    "gl_url",
                    "gl_last_sync",
                    "gl_token",
                ),
            },
        ),
        (
            "Costs",
            {
                "fields": (
                    "hour_rate",
                    "customer_hour_rate",
                    "tax_rate",
                    "daily_work_hours",
                    "annual_paid_work_breaks_days",
                ),
            },
        ),
        ("Notifications", {"fields": ("notify_pipeline_status",)}),
    )
    readonly_fields = ("last_login",)
    change_password_form = AdminPasswordChangeForm
    autocomplete_fields = ("position", "groups")

    @admin_field("Change password")
    def change_password_link(self, instance):
        """Show "Change password" on change form page."""
        return format_html(
            '<a href="{}">change password</a>',  # noqa: P103
            reverse(
                "admin:auth_user_password_change",
                kwargs={"id": instance.pk},
            ),
        )

    def sync_handler(self, user):
        """Syncing user from Gitlab."""
        sync_user_task.delay(user.gl_id)

    def get_default_filters(self, request: HttpRequest) -> Dict[str, str]:
        """Set default filters to the page."""
        return {
            "is_active__exact": "1",
        }
