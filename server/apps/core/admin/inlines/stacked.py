# -*- coding: utf-8 -*-

from admin_tools.mixins import AdminAutocompleteFieldsMixin
from django.contrib import admin

from apps.core.admin.mixins import AdminFieldsOverridesMixin


class BaseStackedInline(
    AdminAutocompleteFieldsMixin,
    AdminFieldsOverridesMixin,
    admin.StackedInline,
):
    """A base class stacked inline."""

    extra = 0
    show_change_link = True
