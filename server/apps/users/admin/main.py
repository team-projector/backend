from urllib.parse import urlparse

from admin_tools.decorators import admin_field
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjUserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils.html import format_html

from apps.core.admin.base import BaseModelAdmin
from apps.core.admin.mixins import AdminFormFieldsOverridesMixin, ForceSyncEntityMixin
from apps.development.tasks import sync_user
from .forms import GroupAdminForm
from ..models import User

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(AdminFormFieldsOverridesMixin,
                ForceSyncEntityMixin,
                DjUserAdmin):
    list_display = (
        'login', 'name', 'email', 'hour_rate', 'last_login', 'is_active', 'is_staff', 'change_password_link'
    )
    list_filter = ('is_active', 'is_staff')
    ordering = ('login',)
    sortable_by = ()
    autocomplete_fields = ('groups',)
    search_fields = ('login',)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'password1', 'password2')}
         ),
    )

    exclude = ('user_permissions',)
    fieldsets = (
        (None, {
            'fields': ('login', 'email', 'name', 'roles', 'is_superuser', 'is_staff', 'is_active', 'last_login')
        }),
        ('GitLab', {
            'fields': ('gl_avatar', 'gl_id', 'gl_url', 'gl_last_sync', 'gl_token')
        }),
        ('Costs', {
            'fields': ('hour_rate', 'customer_hour_rate', 'taxes', 'daily_work_hours')
        })

    )
    readonly_fields = ('last_login',)
    change_password_form = AdminPasswordChangeForm

    @admin_field('Change password')
    def change_password_link(self, obj):
        return format_html(
            '<a href="{}">change password</a>',
            reverse('admin:auth_user_password_change', kwargs={'id': obj.pk})
        )

    def sync_handler(self, obj):
        sync_user.delay(obj.gl_id)

    def changelist_view(self, request, extra_context=None):
        referer = request.META.get('HTTP_REFERER')
        referer_path = urlparse(referer).path

        self._filter_is_active_true_by_default(request, referer, referer_path)

        return super().changelist_view(request, extra_context)

    @staticmethod
    def _filter_is_active_true_by_default(request, referer, referer_path):
        if not referer or referer_path != reverse('admin:users_user_changelist'):
            q = request.GET.copy()
            q['is_active__exact'] = '1'
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()


@admin.register(Group)
class GroupAdmin(BaseModelAdmin):
    list_display = ('name',)
    form = GroupAdminForm
    search_fields = ('name',)
