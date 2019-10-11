# -*- coding: utf-8 -*-

from urllib.parse import urlparse

from admin_tools.decorators import admin_field
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjUserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.urls import reverse
from django.utils.html import format_html

from apps.core.admin.mixins import (
    AdminFormFieldsOverridesMixin,
    ForceSyncEntityMixin,
)
from apps.development.tasks import sync_user

from ..models import User


@admin.register(User)
class UserAdmin(
    AdminFormFieldsOverridesMixin,
    ForceSyncEntityMixin,
    DjUserAdmin,
):
    """A class representing User model for admin dashboard."""

    list_display = (
        'login', 'name', 'email', 'hour_rate', 'last_login', 'is_active',
        'is_staff', 'change_password_link',
    )
    list_filter = ('is_active', 'is_staff')
    ordering = ('login',)
    sortable_by = ()
    search_fields = ('login',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'password1', 'password2'),
        }),
    )

    exclude = ('user_permissions',)
    fieldsets = (
        (None, {
            'fields': (
                'login', 'email', 'name', 'roles', 'is_superuser', 'is_staff',
                'is_active', 'last_login',
            ),
        }),
        ('GitLab', {
            'fields': (
                'gl_avatar', 'gl_id', 'gl_url', 'gl_last_sync', 'gl_token',
            ),
        }),
        ('Costs', {
            'fields': (
                'hour_rate', 'customer_hour_rate', 'taxes', 'daily_work_hours',
            ),
        }),

    )
    readonly_fields = ('last_login',)
    change_password_form = AdminPasswordChangeForm

    @admin_field('Change password')
    def change_password_link(self, user):
        """Show "Change password" on change form page."""
        return format_html(
            '<a href="{}">change password</a>',  # noqa P103
            reverse(
                'admin:auth_user_password_change',
                kwargs={'id': user.pk},
            ),
        )

    def sync_handler(self, user):
        """Syncing user from Gitlab."""
        sync_user.delay(user.gl_id)

    def changelist_view(self, request, extra_context=None):
        """Show only active user by default on change list page."""
        referer = request.META.get('HTTP_REFERER')

        self._apply_default_filter_if_need(request, referer)

        return super().changelist_view(request, extra_context)

    @classmethod
    def _apply_default_filter_if_need(cls, request, referer):
        if cls._is_apply_default_filter(referer):
            query = request.GET.copy()
            query['is_active__exact'] = '1'
            request.GET = query
            request.META['QUERY_STRING'] = request.GET.urlencode()

    @classmethod
    def _is_apply_default_filter(cls, referer) -> bool:
        return (
            not referer or  # noqa: W504
            urlparse(referer).path != reverse('admin:users_user_changelist')
        )
