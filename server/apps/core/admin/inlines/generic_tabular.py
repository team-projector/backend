# -*- coding: utf-8 -*-

from admin_tools.mixins import AdminAutocompleteFieldsMixin
from django.contrib.contenttypes.admin import GenericTabularInline

from apps.core.admin.mixins import AdminFormFieldsOverridesMixin


class BaseGenericTabularInline(
    AdminAutocompleteFieldsMixin,
    AdminFormFieldsOverridesMixin,
    GenericTabularInline,
):
    """A base class generic tabular inline."""

    extra = 0
    show_change_link = True
