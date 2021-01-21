from django.contrib import admin
from jnt_admin_tools.mixins import AutocompleteFieldsAdminMixin

from apps.core.admin.mixins import AdminFieldsOverridesMixin


class BaseStackedInline(
    AutocompleteFieldsAdminMixin,
    AdminFieldsOverridesMixin,
    admin.StackedInline,
):
    """A base class stacked inline."""

    extra = 0
    show_change_link = True
