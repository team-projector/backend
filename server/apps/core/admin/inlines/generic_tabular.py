# -*- coding: utf-8 -*-

from django.contrib.contenttypes.admin import GenericTabularInline
from jnt_admin_tools.mixins import AdminAutocompleteFieldsMixin

from apps.core.admin.mixins import AdminFieldsOverridesMixin


class BaseGenericTabularInline(
    AdminAutocompleteFieldsMixin,
    AdminFieldsOverridesMixin,
    GenericTabularInline,
):
    """A base class generic tabular inline."""

    extra = 0
    show_change_link = True
