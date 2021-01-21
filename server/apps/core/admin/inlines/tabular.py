from django.contrib import admin
from jnt_admin_tools.mixins import AutocompleteFieldsAdminMixin

from apps.core.admin.mixins import AdminFieldsOverridesMixin


class BaseTabularInline(
    AutocompleteFieldsAdminMixin,
    AdminFieldsOverridesMixin,
    admin.TabularInline,
):
    """A base class tabular inline."""

    extra = 0
    show_change_link = True
