# -*- coding: utf-8 -*-

from django.contrib.contenttypes.admin import GenericStackedInline
from jnt_admin_tools.mixins import AdminAutocompleteFieldsMixin

from apps.core.admin.mixins import AdminFieldsOverridesMixin


class BaseGenericStackedInline(
    AdminAutocompleteFieldsMixin,
    AdminFieldsOverridesMixin,
    GenericStackedInline,
):
    """A base class generic stacked inline."""

    extra = 0
    show_change_link = True
