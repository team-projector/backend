# -*- coding: utf-8 -*-

from django.contrib import admin
from jnt_admin_tools.mixins import AdminAutocompleteFieldsMixin

from apps.core.admin.mixins import AdminFieldsOverridesMixin


class BaseTabularInline(
    AdminAutocompleteFieldsMixin,
    AdminFieldsOverridesMixin,
    admin.TabularInline,
):
    """A base class tabular inline."""

    extra = 0
    show_change_link = True
