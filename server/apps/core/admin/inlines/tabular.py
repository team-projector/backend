# -*- coding: utf-8 -*-

from admin_tools.mixins import AdminAutocompleteFieldsMixin
from django.contrib import admin

from apps.core.admin.mixins import AdminFormFieldsOverridesMixin


class BaseTabularInline(
    AdminAutocompleteFieldsMixin,
    AdminFormFieldsOverridesMixin,
    admin.TabularInline,
):
    """A base class tabular inline."""

    extra = 0
    show_change_link = True
